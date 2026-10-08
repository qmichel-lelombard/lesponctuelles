/* Thème d'ambiance original, synthétisé en direct (aucun fichier audio).
   Esprit « space opera » : cordes amples, cor héroïque, harpe, quintes ouvertes.
   Boucle de 32 s en ré majeur : Dmaj9 – Bm(add11) – Gmaj7#11 – Asus4. */
(function () {
  'use strict';
  const BAR = 8, LOOP = BAR * 4;
  const hz = m => 440 * Math.pow(2, (m - 69) / 12);          // note MIDI -> Hz
  const N = { D2: 38, B1: 35, G1: 31, A1: 33, D3: 50, A3: 57, E4: 64, F4s: 66, B3: 59, D4: 62, G3: 55, A4: 69, D5: 74, F5s: 78, E5: 76, B4: 71, C5s: 73, F3s: 54, E3: 52, G4: 67, A5: 81, B5: 83 };
  const CHORDS = [
    { bass: N.D2, pad: [N.D3, N.A3, N.E4, N.F4s, N.A4], arp: [50, 57, 62, 64, 66, 69, 74] },        // Dmaj9
    { bass: N.B1, pad: [N.B3, N.D4, N.F4s, N.A4, 76], arp: [47, 59, 62, 66, 69, 71, 74] },          // Bm(add11)
    { bass: N.G1, pad: [N.G3, N.B3, N.D4, N.F4s, N.C5s], arp: [43, 55, 59, 62, 66, 71, 73] },       // Gmaj7#11
    { bass: N.A1, pad: [N.A3, N.D4, N.E4, N.A4, N.E5], arp: [45, 57, 62, 64, 69, 74, 76] }          // Asus4
  ];
  // mélodie : [mesure, décalage (s), note, durée (s)]
  const MELODY = [
    [0, 0, N.A4, 3.2], [0, 3.6, N.D5, 2.2], [0, 6, N.F5s, 2],
    [1, 0, N.E5, 2.8], [1, 3.2, N.D5, 1.6], [1, 5, N.B4, 3],
    [2, 0, N.B4, 2.6], [2, 3, N.D5, 2], [2, 5.2, N.C5s, 2.8],
    [3, 0, N.E5, 4.2], [3, 4.6, N.D5, 1.6], [3, 6.4, N.A4, 1.6]
  ];

  function voice(ac, out, o) {
    // o : f, t0, dur, type, gain, lp, att, rel, vib, detune
    const g = ac.createGain(), lp = ac.createBiquadFilter();
    lp.type = 'lowpass'; lp.frequency.value = o.lp; lp.Q.value = .5;
    const end = o.t0 + o.dur;
    g.gain.setValueAtTime(0.0001, o.t0);
    g.gain.exponentialRampToValueAtTime(o.gain, o.t0 + o.att);
    g.gain.setValueAtTime(o.gain, Math.max(o.t0 + o.att, end - o.rel * .4));
    g.gain.exponentialRampToValueAtTime(0.0001, end + o.rel);
    const oscs = (o.detune || [0]).map(d => {
      const os = ac.createOscillator(); os.type = o.type; os.frequency.value = o.f; os.detune.value = d;
      if (o.vib) {
        const l = ac.createOscillator(), lg = ac.createGain();
        l.frequency.value = 4.8 + Math.random() * .8; lg.gain.value = o.f * .004; l.connect(lg); lg.connect(os.frequency);
        l.start(o.t0 + o.att); l.stop(end + o.rel + .1);
      }
      os.connect(lp); os.start(o.t0); os.stop(end + o.rel + .1); return os;
    });
    lp.connect(g); g.connect(out); return oscs;
  }

  function pluck(ac, out, f, t0, gain) {
    const o = ac.createOscillator(), o2 = ac.createOscillator(), g = ac.createGain();
    o.type = 'triangle'; o2.type = 'sine'; o.frequency.value = f; o2.frequency.value = f * 2;
    g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(gain, t0 + .012);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.9);
    o.connect(g); o2.connect(g); g.connect(out); o.start(t0); o2.start(t0); o.stop(t0 + 2); o2.stop(t0 + 2);
  }

  /* Programme une boucle complète à partir de t0 (temps du contexte audio).
     dry : bus direct, wet : bus réverbéré, echo : bus d'écho (harpe). */
  function schedule(ac, buses, t0) {
    const { dry, wet, echo } = buses;
    CHORDS.forEach((c, i) => {
      const s = t0 + i * BAR;
      // cordes : accord tenu, attaque lente (swell)
      c.pad.forEach((m, k) => voice(ac, wet, { f: hz(m), t0: s, dur: BAR - .2, type: 'sawtooth', gain: .016, lp: 1500 + k * 120, att: 2.4, rel: 2.8, vib: true, detune: [-9, 8] }));
      // violoncelles / contrebasses
      voice(ac, dry, { f: hz(c.bass), t0: s, dur: BAR - .4, type: 'triangle', gain: .09, lp: 420, att: 1.6, rel: 2.2, detune: [0] });
      voice(ac, wet, { f: hz(c.bass + 12), t0: s, dur: BAR - .4, type: 'sawtooth', gain: .018, lp: 520, att: 1.8, rel: 2.2, vib: true, detune: [-6, 6] });
      // harpe : arpège ascendant puis descendant
      const seq = c.arp.concat(c.arp.slice(1, -1).reverse());
      seq.forEach((m, k) => pluck(ac, echo, hz(m + 12), s + .5 + k * .52, .03 + (k % 3 === 0 ? .012 : 0)));
      // timbales douces et soupir de cymbale au début de la boucle
      if (i === 0) {
        const th = ac.createOscillator(), tg = ac.createGain();
        th.type = 'sine'; th.frequency.setValueAtTime(95, s); th.frequency.exponentialRampToValueAtTime(48, s + .6);
        tg.gain.setValueAtTime(.0001, s); tg.gain.exponentialRampToValueAtTime(.16, s + .02); tg.gain.exponentialRampToValueAtTime(.0001, s + 2.4);
        th.connect(tg); tg.connect(wet); th.start(s); th.stop(s + 2.6);
      }
    });
    // cor héroïque : mélodie
    MELODY.forEach(([bar, off, m, d]) => {
      const s = t0 + bar * BAR + off;
      voice(ac, wet, { f: hz(m), t0: s, dur: d, type: 'sawtooth', gain: .034, lp: 1150, att: .35, rel: .9, vib: true, detune: [-4, 4] });
      voice(ac, dry, { f: hz(m), t0: s, dur: d, type: 'triangle', gain: .02, lp: 1800, att: .3, rel: .8, vib: true, detune: [0] });
    });
  }

  window.MilleMusic = { schedule, LOOP };
})();
