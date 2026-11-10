// npm install; npx playwright install chromium; npm run paper
// Optional module directories let the desktop runtime supply already installed tools.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const resolveFrom=directory=>createRequire(path.join(directory,'package.json'));
const normal=resolveFrom(root);
const runtime=process.env.RENDER_RUNTIME_MODULES?resolveFrom(process.env.RENDER_RUNTIME_MODULES):normal;
const math=process.env.RENDER_MATH_MODULES?resolveFrom(process.env.RENDER_MATH_MODULES):normal;
const {marked}=await import(pathToFileURL(runtime.resolve('marked')).href);
const katex=math('katex');
const {chromium}=runtime('playwright');
const mathBlocks=[];
let source=await fs.readFile(path.join(root,'paper/whitepaper.md'),'utf8');
source=source.replace(/\\\[([\s\S]*?)\\\]/g,(_,s)=>{const key=`MATHTOKEN${mathBlocks.length}END`;mathBlocks.push(katex.renderToString(s,{displayMode:true,throwOnError:true,strict:'error'}));return '\n\n'+key+'\n\n';});
source=source.replace(/\\\(([\s\S]*?)\\\)/g,(_,s)=>{const key=`MATHTOKEN${mathBlocks.length}END`;mathBlocks.push(katex.renderToString(s,{displayMode:false,throwOnError:true,strict:'error'}));return key;});
let body=marked.parse(source);
body=body.replace(/<p>(MATHTOKEN\d+END)<\/p>/g,'$1').replace(/MATHTOKEN(\d+)END/g,(_,i)=>mathBlocks[Number(i)]);
const out=path.join(root,'docs/paper');await fs.mkdir(out,{recursive:true});
const katexDir=path.dirname(math.resolve('katex/package.json'));
await fs.copyFile(path.join(katexDir,'dist/katex.min.css'),path.join(out,'katex.min.css'));
await fs.cp(path.join(katexDir,'dist/fonts'),path.join(out,'fonts'),{recursive:true});
await fs.copyFile(path.join(katexDir,'LICENSE'),path.join(out,'KATEX_LICENSE.txt'));
const css=`@page{size:A4;margin:20mm 19mm 21mm}*{box-sizing:border-box}body{max-width:900px;margin:45px auto;padding:0 30px;color:#172a2c;font:15px/1.65 Georgia,'Times New Roman',serif}h1,h2,h3{font-family:system-ui,sans-serif;line-height:1.25;break-after:avoid}h1{font-size:32px;letter-spacing:-.8px;border-bottom:2px solid #087f76;padding-bottom:20px}h2{font-size:23px;margin-top:35px}h3{font-size:17px;margin-top:25px}a{color:#096b6b;overflow-wrap:anywhere}p{orphans:3;widows:3}table{border-collapse:collapse;width:100%;font-size:12px;margin:20px 0;break-inside:avoid}th,td{border-bottom:1px solid #cad3cb;text-align:left;padding:7px 9px;vertical-align:top}th{background:#edf1e9}code{font:11px/1.4 monospace;overflow-wrap:anywhere}pre{background:#eef1ea;padding:12px;white-space:pre-wrap;break-inside:avoid}img{max-width:100%;height:auto}blockquote{border-left:3px solid #087f76;margin-left:0;padding-left:20px;color:#4a6262}.katex-display{overflow-x:auto;margin:1.3em 0;break-inside:avoid}.katex{font-size:1.04em}nav{font:13px system-ui;margin-bottom:30px}li{margin:5px 0}@media print{body{margin:0;padding:0;font-size:10.1pt;line-height:1.46;color:#111}h1{font-size:23pt}h2{font-size:15pt;margin-top:20pt}h3{font-size:11pt}table{font-size:8.5pt}nav{display:none}.katex-display{overflow:visible}a{color:#075454;text-decoration:none}}`;
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Contextuality Evidence Lab — Research Preprint</title><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="katex.min.css"><style>${css}</style></head><body><nav><a href="../">← Interactive lab</a> · <a href="whitepaper.pdf">Download PDF</a> · <a href="https://github.com/0thernes/contextuality-evidence-lab">Source and proofs</a></nav>${body}</body></html>`;
await fs.writeFile(path.join(out,'index.html'),html);
const browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
try{const page=await browser.newPage();await page.goto(pathToFileURL(path.join(out,'index.html')).href);await page.evaluate(()=>document.fonts.ready);await page.pdf({path:path.join(out,'whitepaper.pdf'),format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#666">Contextuality Evidence Lab · Research preprint · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',margin:{top:'20mm',bottom:'21mm',left:'19mm',right:'19mm'}});await fs.copyFile(path.join(out,'whitepaper.pdf'),path.join(root,'paper/whitepaper.pdf'));console.log(`Rendered ${mathBlocks.length} mathematical expressions and the PDF.`);}finally{await browser.close();}
