const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage();
  await p.goto('file://'+path.resolve(__dirname,'cv.html'));
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(1000);
  // shrink each page's text until both columns fit on one A4 page
  const r = await p.evaluate(()=>[...document.querySelectorAll('.page')].map(pg=>{
    const cols=pg.querySelector('.cols'), kids=[...cols.children]; let fs=8.6;
    const over=()=>Math.max(...kids.map(k=>k.getBoundingClientRect().bottom))-cols.getBoundingClientRect().bottom;
    while (over()>0.5 && fs>7) { fs-=0.1; pg.style.setProperty('--fs',fs.toFixed(1)+'pt'); }
    return [pg.lang, fs.toFixed(1), Math.round(over())];
  }));
  console.log(JSON.stringify(r));
  await p.pdf({path:path.resolve(__dirname,'Quentin-Michel-CV-Poils-et-Plumes-FR-NL-EN.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
  await b.close();
})();
