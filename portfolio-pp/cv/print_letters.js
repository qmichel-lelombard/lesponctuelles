const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage();
  await p.goto('file://'+path.resolve(__dirname,'letters.html'));
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(1000);
  // shrink each page's text until its body fits on one A4 page
  const r = await p.evaluate(()=>[...document.querySelectorAll('.page')].map(pg=>{
    const body=pg.querySelector('.body'); let fs=9.6;
    while (body.scrollHeight>body.clientHeight+1 && fs>7.6) { fs-=0.1; pg.style.setProperty('--fs',fs.toFixed(1)+'pt'); pg.style.fontSize=fs.toFixed(1)+'pt'; }
    return [pg.lang, fs.toFixed(1), body.scrollHeight-body.clientHeight, pg.scrollHeight-pg.clientHeight];
  }));
  console.log(JSON.stringify(r));
  await p.pdf({path:path.resolve(__dirname,'Quentin-Michel-Lettre-de-motivation-Poils-et-Plumes-FR-NL-EN.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
  await b.close();
})();
