import {wins, enumerate, labels, contexts} from './model.mjs';
const $=id=>document.getElementById(id);
let data;
try{const response=await fetch('experiment.json');if(!response.ok)throw new Error(response.status);data=await response.json();}
catch(error){$('replay-summary').textContent='Results unavailable. Serve this directory over HTTP after running the experiment.';throw error;}
$('naive-risk').textContent=(100*data.exact_iid_hitting.naive.decimal).toFixed(2)+'%';
$('safe-risk').textContent=(100*data.exact_iid_hitting.protected.decimal).toFixed(3)+'%';
const series=[{r:data.classical_attack.naive,color:'#bf4d38'}, {r:data.classical_attack.protected,color:'#087f76'}, {r:data.moonlab_readout,color:'#5575be'}];
function chart(fraction=1){
  const w=1000,h=330,l=55,r=15,t=15,b=35;
  const all=series.flatMap(s=>s.r.trace.map(p=>p.log10_capital));
  const lo=Math.floor(Math.min(0,...all)/20)*20,hi=Math.ceil(Math.max(5,...all)/20)*20;
  const x=n=>l+n/6000*(w-l-r),y=v=>h-b-(v-lo)/(hi-lo)*(h-b-t);
  let svg='';
  for(let i=0;i<=5;i++){const v=lo+(hi-lo)*i/5;svg+=`<line x1="${l}" y1="${y(v)}" x2="${w-r}" y2="${y(v)}" stroke="#d5dcd3"/><text x="${l-8}" y="${y(v)+4}" text-anchor="end" fill="#536a6b" font-size="11">${v.toFixed(0)}</text>`;}
  for(let n=0;n<=6000;n+=1000)svg+=`<text x="${x(n)}" y="${h-8}" text-anchor="middle" fill="#536a6b" font-size="11">${n}</text>`;
  svg+=`<line x1="${l}" y1="${y(2)}" x2="${w-r}" y2="${y(2)}" stroke="#142b2d" stroke-dasharray="5 5"/><text x="${w-r}" y="${y(2)-7}" text-anchor="end" fill="#142b2d" font-size="11">evidence 100</text>`;
  for(const s of series){const points=s.r.trace.filter(p=>p.trial<=6000*fraction).map(p=>`${x(p.trial)},${y(p.log10_capital)}`).join(' ');svg+=`<polyline points="${points}" fill="none" stroke="${s.color}" stroke-width="2.5"/>`;}
  $('chart').innerHTML=svg;
}
chart();
let animation=0;
$('replay').onclick=()=>{cancelAnimationFrame(animation);const start=performance.now();function step(now){const f=Math.min(1,(now-start)/1800);chart(f);if(f<1)animation=requestAnimationFrame(step);}animation=requestAnimationFrame(step);};
$('replay-summary').textContent=`In the recorded attack, the naive test first crosses at trial ${data.classical_attack.naive.first_crossing}; the corrected test ${data.classical_attack.protected.first_crossing===null?'never crosses':`crosses at trial ${data.classical_attack.protected.first_crossing}`}. Moonlab's noisy simulated run crosses the corrected threshold at trial ${data.moonlab_readout.first_crossing}, with ${data.moonlab_readout.successes.toLocaleString()} / 6,000 successful contexts.`;
let mask=0;
function update(){
  $('square').innerHTML=labels.map((label,i)=>`<button data-index="${i}" class="${(mask>>i)&1?'negative':''}" aria-label="Flip ${label}"><span>${label}</span><b>${(mask>>i)&1?'−1':'+1'}</b></button>`).join('');
  for(const el of $('square').children)el.onclick=()=>{mask^=1<<Number(el.dataset.index);update();};
  const k=Number($('floor').value),p=k/60,other=(1-p)/5,success=wins(mask);
  $('floor-label').textContent=`${k}/60 (${(100*p).toFixed(2)}%)`;
  $('contexts').innerHTML=contexts.map((c,i)=>`<div class="${success[i]?'':'fail'}"><span>${i<3?'ROW':'COL'} ${i%3+1}: ${c.map(j=>labels[j]).join(' · ')}</span><span>${success[i]?'PASS':'FAIL'}</span></div>`).join('');
  const score=success.reduce((s,win,i)=>s+(win?(i===5?p:other):0),0),bound=1-Math.min(p,other);
  $('score').textContent=`This table: ${(100*score).toFixed(2)}% wins · sharp classical maximum: ${(100*bound).toFixed(2)}%`;
}
$('floor').oninput=update;update();
$('enumerate').onclick=()=>{const h=enumerate();$('enumeration').textContent=`Verified in this browser: ${h[1]} tables fail 1 context, ${h[3]} fail 3, ${h[5]} fail 5. No table wins every context.`;};
$('bad-floor').onclick=()=>{$('control-result').textContent='CERTIFICATE REJECTED: the claimed floor 1/6 exceeds the actual final-setting probability 1/12. Calibrating to the unsupported floor produces a 97.24% false-rejection probability by trial 1,000, despite a nominal 1% threshold.';};
$('leak').onclick=()=>{$('control-result').textContent=`OUTSIDE THE MODEL: after seeing the selected context, the device can choose a table that fails a different context. It wins every time and crosses even the corrected threshold at trial ${data.context_leak_outside_model.first_crossing}. The certificate cannot establish setting independence from a transcript; this attack deliberately violates that assumption.`;};
$('reset-control').onclick=()=>{$('control-result').textContent='Choose a falsification control to inspect what the certificate does and does not protect.';};
