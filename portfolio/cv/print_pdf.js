const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  for (const [src,out] of [['letters.html','Quentin-Michel-Lettre-de-motivation-FR-NL-EN.pdf'],['cv.html','Quentin-Michel-CV-FR-EN.pdf']]) {
    const p = await b.newPage();
    await p.goto('file://'+path.resolve(__dirname,src));
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(1200);
    const ov = await p.evaluate(()=>[...document.querySelectorAll('.page')].map(pg=>{const m=pg.querySelector('.letter,.cols');return [pg.scrollHeight-pg.clientHeight, m? m.scrollHeight-m.clientHeight:0]}));
    console.log(src, JSON.stringify(ov));
    await p.pdf({path:path.resolve(__dirname,out),format:'A4',printBackground:true,preferCSSPageSize:true});
  }
  await b.close();
})();
