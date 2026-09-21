const fs=require('fs'),vm=require('vm'),assert=require('assert');
vm.runInThisContext(fs.readFileSync(__dirname+'/panorama-finder.js','utf8'));
const {route,fourDice,eligible,appeal}=globalThis.Panorama;
const reached=new Set();let checks=0;
for(let d=1;d<=6;d++)for(let r=1;r<=5;r++)for(let c=1;c<=8;c++){
  reached.add(route(d,r,c).id);
  for(let z=-4;z<=4;z++)for(let s=0;s<=2;s++)for(const b of[0,2]){
    const x=route(d,r,c,z,s,b);assert(x.local>=1&&x.local<=40);assert.strictEqual(Math.floor((Number(x.id.slice(1))-1)/40)+1,d);checks++;
  }
}
assert.strictEqual(reached.size,240);assert(reached.has('P001')&&reached.has('P240'));
assert.strictEqual(route(3,1,2,-3,1,0).id,'P120'); // Printed worked example wraps backwards.
assert.strictEqual(route(6,5,8,4,2,2).id,'P208'); // Last shelf wraps without changing department.
assert.strictEqual(fourDice([1,2,3,5]),-1);assert.strictEqual(fourDice([6,6,6,6]),4);
assert.throws(()=>fourDice([0,6,6,6]));assert.throws(()=>route(0,1,1));assert.throws(()=>route(1,6,1));assert.throws(()=>route(1,1,1,0,0,1));
assert.strictEqual(appeal(route(1,1,1),-1).id,'P040');assert.throws(()=>appeal(route(1,1,1),1,1));
assert.throws(()=>appeal(appeal(route(1,1,1),1),1));
assert.strictEqual(Panorama.appealDepartment(route(1,2,1),4).id,'P129');
assert.throws(()=>Panorama.appealDepartment(appeal(route(1,1,1),1),3));
const ordinary={pace:'waits',native_coop:'no',memory:'unknown',fit_tier:'promising'};
assert.strictEqual(eligible(ordinary,{},{}),true);
for(const k of['untimed','camera','mouse','coop','memory'])assert.strictEqual(eligible(ordinary,{}, {[k]:true}),false,k);
assert.strictEqual(eligible(ordinary,{developer_declarations:['Playable without Timed Input']},{untimed:true}),true);
assert.strictEqual(eligible(ordinary,{developer_declarations:['Playable without Timed Input']},{untimed:true,camera:true}),false);
console.log(JSON.stringify({reachableCases:reached.size,modifierAddressesChecked:checks,printedExamples:'passed',vetoFilters:'fail closed on unknown',appealLimit:'passed',invalidInputs:'rejected'},null,2));
