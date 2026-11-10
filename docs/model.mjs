export const contexts = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]];
export const labels = ['XI','IX','XX','IZ','ZI','ZZ','XZ','ZX','YY'];
export function wins(mask) {
  return contexts.map((c,i) => (c.reduce((s,j)=>s+((mask>>j)&1),0)%2) === (i===5?1:0));
}
export function enumerate() {
  const histogram = {1:0,3:0,5:0};
  for(let m=0;m<512;m++) histogram[wins(m).filter(x=>!x).length]++;
  return histogram;
}
export function exactReplay(trials, an, ad, bn, bd, threshold=100n) {
  let numerator=1n,denominator=1n,first=null;
  for (let i=0;i<trials.length;i++) {
    numerator*=trials[i]?an:bn; denominator*=trials[i]?ad:bd;
    if(first===null && numerator>=threshold*denominator) first=i+1;
  }
  return first;
}
