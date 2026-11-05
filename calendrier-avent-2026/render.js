// usage: node render.js config.json out.png
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const cfg=JSON.parse(fs.readFileSync(process.argv[2]));const dir=path.dirname(path.resolve(process.argv[2]));
const u=f=>'file://'+path.resolve(dir,f);
let books='';
for(const b of cfg.books){
 const t=b.t||20;
 books+=`<div class="shadow" style="left:${b.x-10+(b.sx||0)}px;top:${b.y+b.h-28}px;width:${b.w+70}px;height:56px"></div>
 <div class="stage"><div class="book" style="--t:${t}px;left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;transform:rotateY(${b.ry}deg) rotateZ(${b.rz||0}deg)">
 <div class="face bk" style="transform:translateZ(-${t}px) rotateY(180deg)"></div>
 <div class="face sp" style="width:${t}px;left:${-t/2}px;background-image:url(${u(b.img)});background-size:auto 100%;background-position:left;transform:translateZ(-${t/2}px) rotateY(-90deg)"></div>
 <div class="face pg" style="width:${t}px;left:${b.w-t/2-2}px;transform:translateZ(-${t/2}px) rotateY(90deg)"></div>
 <div class="face tp" style="height:${t}px;top:${-t/2+2}px;transform:translateZ(-${t/2}px) rotateX(90deg)"></div>
 <div class="face bt" style="height:${t}px;top:${b.h-t/2}px;transform:translateZ(-${t/2}px) rotateX(-90deg)"></div>
 <div class="f" style="background-image:url(${u(b.img)})"></div></div></div>`;
}
let html=fs.readFileSync(path.join(__dirname,'visuel.html'),'utf8').replace('FONT_URL',u(cfg.font)).replace('BG_URL',u(cfg.bg))
 .replace('BOOKS',books).replace('DATE',cfg.date).replace('LEFT',cfg.dateX).replace('TOP',cfg.dateY);
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
 const tmp=path.join(dir,'_page.html');fs.writeFileSync(tmp,html);await p.goto('file://'+tmp);await p.evaluate(()=>document.fonts.ready);
 await p.waitForTimeout(300);await p.screenshot({path:process.argv[3]});await br.close();})();
