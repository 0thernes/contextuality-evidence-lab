/** Native pinned Moonlab gates, Pauli measurements and collapse.
 * Seeded Tsotchke quantum_rng supplies draws; everything runs classically.
 * This wrapper is coupled to the pinned WASM32 state layout (pointer +8).
 */
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require=createRequire(import.meta.url);
const M=await require(path.join(root,'third_party/moonlab/moonlab.js'))({print:()=>{},printErr:()=>{}});
const seed=Number(process.argv[2]??20261110), n=Number(process.argv[3]??6000);
if(!Number.isSafeInteger(seed)||seed<0||seed>=Number.MAX_SAFE_INTEGER)throw Error('invalid seed');
if(!Number.isInteger(n)||n<1||n>100000)throw Error('trials must be 1..100000');
const streamSize=Math.max(1048576,128*n+131072);
const qr=path.join(root,'build',process.platform==='win32'?'stack_qrng.exe':'stack_qrng');
const bytes=Buffer.from(execFileSync(qr,[String(seed),String(streamSize)],{maxBuffer:2*streamSize+1024}).toString(),'hex');
let cursor=0,gateCount=0,measurements=0,rejectedDraws=0;
function assert(x,msg){if(!x)throw Error(msg);}
function u32(){assert(cursor+4<=bytes.length,'QRNG stream exhausted');const r=bytes.readUInt32LE(cursor);cursor+=4;return r;}
function unit(){return (u32()>>>8)/16777216;}
// Uniform integer extraction from a uniform 32-bit input: reject the tail.
// This removes mapping bias; it does not establish the mixer's entropy quality.
function below(n){const limit=0x100000000-(0x100000000%n);let r;do{r=u32();if(r>=limit)rejectedDraws++;}while(r>=limit);return r%n;}
function state(){const p=M._malloc(256);M.HEAPU8.fill(0,p,p+256);assert(M._quantum_state_init(p,2)===0,'state init');return p;}
function free(p){M._quantum_state_free(p);M._free(p);}
function clone(p){const q=M._malloc(256);M.HEAPU8.fill(0,q,q+256);assert(M._quantum_state_clone(q,p)===0,'state clone');return q;}
function amplitudes(p){const b=M.HEAPU32[(p+8)>>2]>>3;return Array.from({length:4},(_,i)=>[M.HEAPF64[b+2*i],M.HEAPF64[b+2*i+1]]);}
function gate(name,...args){M[name](...args);gateCount++;}
const observables=['XI','IX','XX','IZ','ZI','ZZ','XZ','ZX','YY'];
const contexts=[{indices:[0,1,2],sign:1},{indices:[3,4,5],sign:1},{indices:[6,7,8],sign:1},
 {indices:[0,3,6],sign:1},{indices:[1,4,7],sign:1},{indices:[2,5,8],sign:-1}];
const multiply={II:[0,'I'],IX:[0,'X'],IY:[0,'Y'],IZ:[0,'Z'],XI:[0,'X'],XX:[0,'I'],XY:[1,'Z'],XZ:[3,'Y'],
 YI:[0,'Y'],YX:[3,'Z'],YY:[0,'I'],YZ:[1,'X'],ZI:[0,'Z'],ZX:[1,'Y'],ZY:[3,'X'],ZZ:[0,'I']};
function pauliProduct(words){let out='II',phase=0;for(const word of words){let next='';for(let q=0;q<2;q++){
 const [p,c]=multiply[out[q]+word[q]];phase+=p;next+=c;}out=next;}return [phase%4,out];}
function validSign(c){const [p,w]=pauliProduct(c.indices.map(i=>observables[i]));return w==='II'&&p===(c.sign===1?0:2);}
for(const c of contexts){assert(validSign(c),'exact Pauli product sign');assert(!validSign({...c,sign:-c.sign}),'sign mutation escaped');
 for(const a of c.indices)for(const b of c.indices)assert(JSON.stringify(pauliProduct([observables[a],observables[b]]))===JSON.stringify(pauliProduct([observables[b],observables[a]])),'noncommuting context');}
function rotate(p,word){let t=-1;for(let q=0;q<2;q++){if(word[q]==='I')continue;if(t<0)t=q;
 if(word[q]==='Y')gate('_gate_s_dagger',p,q);if(word[q]==='X'||word[q]==='Y')gate('_gate_hadamard',p,q);}
 for(let q=0;q<2;q++)if(q!==t&&word[q]!=='I')gate('_gate_cnot',p,q,t);return t;}
function unrotate(p,word,t){for(let q=1;q>=0;q--)if(q!==t&&word[q]!=='I')gate('_gate_cnot',p,q,t);
 for(let q=0;q<2;q++){if(word[q]==='X'||word[q]==='Y')gate('_gate_hadamard',p,q);if(word[q]==='Y')gate('_gate_s',p,q);}}
function measure(p,word){const t=rotate(p,word),bit=M._measurement_single_qubit(p,t,unit());
 assert(bit===0||bit===1,'measurement returned invalid bit');measurements++;unrotate(p,word,t);return bit===0?1:-1;}
function expectation(p,word){const q=clone(p),t=rotate(q,word),e=M._measurement_expectation_z(q,t);free(q);return e;}
function directExpectation(amps,word){let a=0,z=0,ys=0;for(let q=0;q<2;q++){if('XY'.includes(word[q]))a|=1<<q;if('ZY'.includes(word[q]))z|=1<<q;if(word[q]==='Y')ys++;}
 const phases=[[1,0],[0,1],[-1,0],[0,-1]];let re=0;for(let x=0;x<4;x++){let p=0,v=x&z;while(v){p^=v&1;v>>=1;}
 const [pr,pi]=phases[(ys+2*p)%4],[ar,ai]=amps[x],[br,bi]=amps[x^a];re+=br*(pr*ar-pi*ai)+bi*(pr*ai+pi*ar);}return re;}
function prepare(kind,component=0){const p=state();
 if(kind==='plus')for(let q=0;q<2;q++)gate('_gate_hadamard',p,q);
 if(kind==='bell'){gate('_gate_hadamard',p,0);gate('_gate_cnot',p,0,1);}
 if(kind==='complex')for(let layer=0;layer<2;layer++){for(let q=0;q<2;q++){gate('_gate_ry',p,q,2*Math.PI*unit());gate('_gate_rz',p,q,2*Math.PI*unit());}gate('_gate_cnot',p,0,1);}
 if(kind==='basis')for(let q=0;q<2;q++)if(component&(1<<q))gate('_gate_pauli_x',p,q);
 return p;}
function shuffled(xs){const order=[...xs];for(let j=order.length-1;j>0;j--){const k=below(j+1);[order[j],order[k]]=[order[k],order[j]];}return order;}
let oracleError=0,repeatFailures=0,idealShots=0,flippedSignRejections=0;
const checks=[];
for(const kind of ['zero','plus','bell','complex','basis']){
 const components=kind==='basis'?4:1;let trials=0,agreed=0;
 for(let component=0;component<components;component++){const p=prepare(kind,component),amps=amplitudes(p);
  for(const word of observables){oracleError=Math.max(oracleError,Math.abs(expectation(p,word)-directExpectation(amps,word)));
   const q=clone(p),a=measure(q,word),b=measure(q,word);repeatFailures+=Number(a!==b);free(q);}
  for(const c of contexts)for(let shot=0;shot<16;shot++){const q=clone(p);let parity=1;
   for(const i of shuffled(c.indices))parity*=measure(q,observables[i]);free(q);trials++;agreed+=Number(parity===c.sign);flippedSignRejections+=Number(parity!==-c.sign);}
  free(p);}
 assert(agreed===trials,'ideal state-independence implementation test');idealShots+=trials;checks.push({preparation:kind,components,trials,agreed});}
assert(oracleError<1e-12&&repeatFailures===0,'Pauli oracle or repeatability check');
const trials=[],shots=[],contextCounts=Array(6).fill(0),sampleState=prepare('complex');
let flips=0,noisySuccesses=0;
for(let t=0;t<n;t++){const context=below(6),c=contexts[context],q=clone(sampleState),order=shuffled(c.indices);
 const ideal=[],recorded=[],readoutFlips=[];contextCounts[context]++;
 for(const i of order){const a=measure(q,observables[i]),flip=below(100)===0;ideal.push(a);recorded.push(flip?-a:a);readoutFlips.push(flip);flips+=Number(flip);}
 free(q);assert(ideal.reduce((a,b)=>a*b,1)===c.sign,'sampled ideal identity failed');
 const success=recorded.reduce((a,b)=>a*b,1)===c.sign;noisySuccesses+=Number(success);
 trials.push({context,success});shots.push({context,order,ideal_outcomes:ideal,recorded_outcomes:recorded,readout_flips:readoutFlips,success});}
free(sampleState);
const parameters=[0.37,1.23,-0.43,0.61];
function paramState(values){const p=state();for(let q=0;q<2;q++){gate('_gate_ry',p,q,values[q]);gate('_gate_rz',p,q,values[q+2]);}
 // Fixed unitary leaves the product-family QGT unchanged.
 gate('_gate_cnot',p,0,1);const a=amplitudes(p);free(p);return a;}
const h=1e-5,stateValues=paramState(parameters),tangents=[];
for(let j=0;j<4;j++){const plus=[...parameters],minus=[...parameters];plus[j]+=h;minus[j]-=h;
 const ap=paramState(plus),am=paramState(minus);tangents.push(ap.map((v,k)=>v.map((x,c)=>(x-am[k][c])/(2*h))));}
mkdirSync(path.join(root,'results'),{recursive:true});
const save=(name,value)=>writeFileSync(path.join(root,'results',name),JSON.stringify(value,null,2)+'\n');
save('stack_trials.json',trials);save('stack_shots.json',shots);save('stack_tangents.json',{parameters,step:h,state:stateValues,tangents});
const report={status:'pass',engine:'Pinned Tsotchke Moonlab classical CPU/WASM simulator',qubits:2,observables,contexts,
 exact_operator_sign_checks:6,operator_sign_mutation_rejections:6,ideal_state_checks:checks,ideal_check_shots:idealShots,
 sampled_ideal_successes:n,max_pauli_expectation_oracle_error:oracleError,repeated_measurement_failures:repeatFailures,
 flipped_sign_shot_rejections:flippedSignRejections,gate_calls:gateCount,projective_measurements:measurements,
 sampled_trials:n,context_counts:contextCounts,noisy_successes:noisySuccesses,noisy_failures:n-noisySuccesses,readout_flips:flips,
 noise:{per_observable_flip_probability:0.01,idealized_independent_parity_success_probability:(1+0.98**3)/2,
 mechanism:'Independent fresh seeded mixer draws, rejection-sampled integer 0..99, flip if zero; independence is a simulation model assumption, not certified entropy.'},
 qrng:{seed,consumed_bytes:cursor,stream_bytes:bytes.length,rejection_sampling_discarded_words:rejectedDraws,
 sha256:createHash('sha256').update(bytes).digest('hex'),classification:'Seeded classical software mixer; no physical quantum entropy'},
 wasm_sha256:createHash('sha256').update(readFileSync(path.join(root,'third_party/moonlab/moonlab.wasm'))).digest('hex'),
 setting_scope:'Integer rejection sampling removes modulo mapping bias given uniform input words. This deterministic software stream does not establish experimental measurement independence.',
 state_scope:'Finite native simulation probes. Exact context Pauli products supply the algebraic ideal-state claim; these shots are not quantum hardware evidence.'};
save('stack_moonlab.json',report);console.log(JSON.stringify(report));
