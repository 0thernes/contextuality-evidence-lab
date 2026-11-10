import assert from 'node:assert/strict';
import {enumerate,wins,exactReplay} from '../docs/model.mjs';
assert.deepEqual(enumerate(),{1:96,3:320,5:96});
assert.deepEqual(wins(0),[true,true,true,true,true,false]);
assert.equal(exactReplay(Array(36).fill(true),57n,50n,3n,10n),36);
assert.equal(exactReplay(Array(36).fill(true),57n,55n,3n,5n),null);
assert.equal(exactReplay(Array(600).fill(true),57n,55n,3n,5n),129);
console.log('Browser model: enumeration and exact BigInt threshold checks passed.');
