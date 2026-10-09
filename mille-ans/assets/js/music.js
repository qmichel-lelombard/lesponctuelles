/* Ambiance « space ambient » originale, synthétisée en direct (aucun fichier audio).
   Nappes sombres, basse profonde, séquenceur lent en écho, cloches cristallines.
   Boucle de 64 s en ré mineur : Dm9 – Bbmaj7 – Gm9 – A(sus4). */
(function () {
  'use strict';
  const BAR = 16, LOOP = BAR * 4;
  const hz = m => 440 * Math.pow(2, (m - 69) / 12);
  const CH = [
    { bass: 38, pad: [50, 57, 60, 64, 69], seq: [62, 65, 69, 72, 74, 72, 69, 65], bell: [81, 84, 88] },   // Dm9
    { bass: 34, pad: [46, 53, 57, 62, 65], seq: [58, 62, 65, 69, 70, 69, 65, 62], bell: [77, 81, 86] },   // Bbmaj7
    { bass: 31, pad: [43, 50, 55, 58, 62], seq: [55, 58, 62, 65, 67, 65, 62, 58], bell: [79, 82, 86] },   // Gm9
    { bass: 33, pad: [45, 50, 52, 57, 64], seq: [57, 61, 64, 69, 71, 69, 64, 61], bell: [81, 85, 88] }    // Asus4
  ];

  function pad(ac, out, f, t0, dur, g, cut) {
    const lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.Q.value = 1.2;
    lp.frequency.setValueAtTime(cut * .35, t0);
    lp.frequency.linearRampToValueAtTime(cut, t0 + dur * .5);
    lp.frequency.linearRampToValueAtTime(cut * .4, t0 + dur);
    const gn = ac.createGain();
    gn.gain.setValueAtTime(.0001, t0);
    gn.gain.exponentialRampToValueAtTime(g, t0 + 4);
    gn.gain.setValueAtTime(g, t0 + dur - 4);
    gn.gain.exponentialRampToValueAtTime(.0001, t0 + dur + 3);
    [-11, 0, 9].forEach(d => {
      const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f; o.detune.value = d;
      o.connect(lp); o.start(t0); o.stop(t0 + dur + 3.2);
    });
    lp.connect(gn); gn.connect(out);
  }
  function note(ac, out, f, t0, g, len, type, cut) {
    const o = ac.createOscillator(), gn = ac.createGain(), lp = ac.createBiquadFilter();
    o.type = type; o.frequency.value = f; lp.type = 'lowpass'; lp.Q.value = 6;
    lp.frequency.setValueAtTime(cut, t0); lp.frequency.exponentialRampToValueAtTime(Math.max(200, cut * .2), t0 + len);
    gn.gain.setValueAtTime(.0001, t0); gn.gain.exponentialRampToValueAtTime(g, t0 + .02); gn.gain.exponentialRampToValueAtTime(.0001, t0 + len);
    o.connect(lp); lp.connect(gn); gn.connect(out); o.start(t0); o.stop(t0 + len + .1);
  }
  function bell(ac, out, f, t0, g) {
    [1, 2.76, 5.4].forEach((r, i) => {
      const o = ac.createOscillator(), gn = ac.createGain();
      o.type = 'sine'; o.frequency.value = f * r;
      gn.gain.setValueAtTime(.0001, t0); gn.gain.exponentialRampToValueAtTime(g / (i + 1), t0 + .01); gn.gain.exponentialRampToValueAtTime(.0001, t0 + 5 - i);
      o.connect(gn); gn.connect(out); o.start(t0); o.stop(t0 + 5.2);
    });
  }

  function schedule(ac, buses, t0) {
    const { dry, wet, echo } = buses;
    CH.forEach((c, i) => {
      const s = t0 + i * BAR;
      c.pad.forEach((m, k) => pad(ac, wet, hz(m), s, BAR, .02, 900 + k * 220));
      // sub-basse : deux notes tenues
      [0, 8].forEach(off => note(ac, dry, hz(c.bass), s + off, .16, 7.5, 'sine', 400));
      note(ac, dry, hz(c.bass + 12), s, .035, 15, 'triangle', 500);
      // séquenceur croche lente, accentué un pas sur quatre
      for (let n = 0; n < 24; n++) {
        const m = c.seq[n % c.seq.length] + (n % 8 === 7 ? 12 : 0);
        note(ac, echo, hz(m), s + 1 + n * .66, n % 4 === 0 ? .05 : .028, .6, 'sawtooth', 1900 + 600 * Math.sin(n / 4));
      }
      // cloches
      c.bell.forEach((m, k) => bell(ac, echo, hz(m), s + 2.5 + k * 4.7, .018));
    });
    // grosse pulsation grave au début de la boucle
    const s = t0, o = ac.createOscillator(), gn = ac.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(70, s); o.frequency.exponentialRampToValueAtTime(34, s + 1.6);
    gn.gain.setValueAtTime(.0001, s); gn.gain.exponentialRampToValueAtTime(.22, s + .03); gn.gain.exponentialRampToValueAtTime(.0001, s + 4);
    o.connect(gn); gn.connect(wet); o.start(s); o.stop(s + 4.2);
  }
  window.MilleMusic = { schedule, LOOP };
})();
