"""Bande-son synthétique (128 BPM, 30 s) calée sur le montage de promo.html.

Un album = une mesure de 4 temps ; changement d'accord à chaque album,
souffle (whoosh) avant chaque entrée, impact à la fin de l'intro et sur le logo.
usage : python3 soundtrack.py 2026-11 [6]   (écrit out/soundtrack-2026-11[-long].wav, données dans months.js ;
        le 2e argument = temps par album, 4 par défaut)
"""
import json
import pathlib
import subprocess
import sys
import wave

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MONTH = sys.argv[1] if len(sys.argv) > 1 else '2026-10'
SLOT_BEATS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
SFX = '' if SLOT_BEATS == 4 else '-long'
albums = json.loads(subprocess.check_output(
    ['node', '-e', 'global.window={};require(process.argv[1]);'
     'console.log(JSON.stringify(window.MONTHS[process.argv[2]].albums))',
     str(HERE / 'months.js'), MONTH]))
N_ALB = len(albums)
GROUP_STARTS = [i for i in range(1, N_ALB) if albums[i]['d'] != albums[i - 1]['d']]

# même découpage que promo.html : SLOT_BEATS temps par album, le reste partagé entre intro et outro
SR = 44100
BEAT = 60 / 128
SPARE = max(0, 64 - SLOT_BEATS * N_ALB - 16)
INTRO_BEATS = 8 + (SPARE // 8) * 4
DUR = max(64, INTRO_BEATS + SLOT_BEATS * N_ALB + 8) * BEAT
INTRO = INTRO_BEATS * BEAT
SLOT = SLOT_BEATS * BEAT
OUTRO = INTRO + N_ALB * SLOT
STRETCH = INTRO / (8 * BEAT)
N = int(DUR * SR) + SR
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    mix[i:i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
    mix[i:i + len(sig), 1] += sig * gain * (1 + min(pan, 0))


def lowpass(x, cutoff):
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.16)


def hat(n_s=0.06):
    n = int(n_s * SR)
    x = rng.standard_normal(n)
    x = x - lowpass(x, 7000)
    return x * env(n, 0.001, 0.018)


def clap():
    n = int(0.25 * SR)
    x = rng.standard_normal(n)
    x = lowpass(x, 3500) - lowpass(x, 900)
    e = env(n, 0.001, 0.07)
    for d in (0.008, 0.018):
        e[: int(d * SR)] *= 0.6
    return x * e * 2.5


def saw(freq, n):
    t = np.arange(n) / SR
    return 2 * ((t * freq) % 1) - 1


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def pad(chord, dur):
    n = int(dur * SR)
    x = sum(saw(note(m) * d, n) for m in chord for d in (0.997, 1.003))
    x = lowpass(x / (2 * len(chord)), 1400)
    t = np.arange(n) / SR
    return x * np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.15).clip(0)


def bass(m, dur):
    n = int(dur * SR)
    x = lowpass(saw(note(m), n), 380) + 0.6 * np.sin(2 * np.pi * note(m) * np.arange(n) / SR)
    return x * env(n, 0.005, dur * 0.6)


def pluck(m, dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * note(m) * t) + 0.3 * np.sin(4 * np.pi * note(m) * t)
    return x * env(n, 0.002, 0.18)


def whoosh(length, rise=True):
    n = int(length * SR)
    x = rng.standard_normal(n)
    k = np.linspace(0, 1, n)
    shape = k ** 2 if rise else (1 - k) ** 2
    return lowpass(x, 300 + 6000 * shape) * shape * 0.8


def impact():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 12)) / SR) * np.exp(-t * 2.2)
    noise = lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 6)
    return sub + 0.4 * noise


# progression (une mesure par album) : Am F C G | Am F C E | Dm F G Am
PROG = [
    (57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (55, [55, 59, 62, 67]),
    (57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (52, [56, 59, 64, 68]),
    (50, [57, 62, 65, 69]), (53, [57, 60, 65, 69]), (55, [55, 59, 62, 67]), (57, [57, 60, 64, 69]),
]
MELO = [76, 74, 72, 74, 76, 77, 79, 80, 77, 81, 79, 76]
if N_ALB != len(PROG):   # on garde le début de la grille et on finit sur G pour retomber sur Am à l'outro
    PROG = (PROG * 2)[:N_ALB - 1] + [(55, [55, 59, 62, 67])]
    MELO = (MELO * 2)[:N_ALB - 1] + [79]

# --- intro : nappe + montée + décodage
add(pad([57, 64, 69, 72], INTRO), 0, 0.35)
add(whoosh(INTRO - 0.2), 0.2, 0.25)
for i, m in enumerate([69, 72, 76, 79, 81, 84, 88]):
    add(pluck(m, 0.4), (0.35 + i * 0.07 + 0.4) * STRETCH, 0.12, pan=(i - 3) * 0.12)
for i in range(4):
    add(hat(0.03), (1.35 + i * 0.12) * STRETCH, 0.25)
add(impact(), INTRO, 0.55)

# --- albums
for a, (b, ch) in enumerate(PROG):
    t0 = INTRO + a * SLOT
    add(pad(ch, SLOT), t0, 0.28)
    add(whoosh(0.45), t0 - 0.45, 0.22, pan=0.3 if a % 2 else -0.3)
    add(pluck(MELO[a], 0.7), t0 + 0.12, 0.16)
    add(pluck(MELO[a] - 12, 0.7), t0 + 0.12 + BEAT * 1.5, 0.08)
    if SLOT_BEATS > 4:   # version longue : la mélodie revient sur la 2e moitié de l'album
        add(pluck(MELO[a] + 7, 0.7), t0 + 4 * BEAT + 0.12, 0.1)
    for k in range(SLOT_BEATS):
        tb = t0 + k * BEAT
        add(kick(), tb, 0.8)
        add(bass(b, BEAT * 0.9), tb + BEAT / 2, 0.22)
        add(hat(), tb + BEAT / 2, 0.22, pan=0.25)
        add(hat(0.03), tb + BEAT * 0.75, 0.09, pan=-0.25)
        if k % 2 == 1:
            add(clap(), tb, 0.32)

# --- changements de date : petit impact
for a in GROUP_STARTS:
    add(impact(), INTRO + a * SLOT, 0.22)

# --- outro : envolée de couvertures + logo
add(whoosh(0.5), OUTRO - 0.5, 0.3)
add(impact(), OUTRO, 0.4)
add(pad([57, 64, 69, 72, 76], DUR - OUTRO + 0.5), OUTRO, 0.33)
for i in range(11):
    add(pluck(81 + [0, 3, 7, 12][i % 4], 0.3), OUTRO + 0.05 + i * 0.045, 0.06, pan=(i - 5) * 0.15)
add(impact(), OUTRO + 1.15, 0.35)
for m in (69, 76, 81, 88):
    add(pluck(m, 2.5), OUTRO + 1.15, 0.12)

# --- master
mix = mix[: int(DUR * SR)]
fade = np.ones(len(mix))
nf = int(1.2 * SR)
fade[-nf:] = np.linspace(1, 0, nf) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / 0.89
pcm = (mix * 32767).astype(np.int16)
(HERE / 'out').mkdir(exist_ok=True)
with wave.open(str(HERE / 'out' / f'soundtrack-{MONTH}{SFX}.wav'), 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('ok', len(pcm) / SR, 's')
