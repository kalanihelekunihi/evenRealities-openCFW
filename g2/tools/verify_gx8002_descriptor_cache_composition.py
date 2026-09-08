#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compose decoded descriptor wrapper with decoded cache-clean MMIO loops."""
import json,hashlib
from itertools import product
import verify_gx8002_snpu_task_cmd_cache_flush as wrapper
import verify_gx8002_dcache_clean_range as clean

def composed(wrapper_code,wrapper_pc,delta,clean_code,clean_pc,pointer,seed):
    trace=[]
    def call(address,length,stack):
        writes,returned=clean.execute(clean_code,clean_pc,address,length,seed,stack_top=stack)
        if not returned:raise ValueError('cache nested termination')
        trace.extend(writes)
    wrapper.execute(wrapper_code,wrapper_pc,delta,pointer,seed,clean_call=call)
    return trace

def verify():
    wrapper.verify();clean.verify();wo,wn=wrapper.programs();co,cn=clean.programs();cases=0
    for pointer in (0,1,0x20027360,0x20027870,0xfffffff0,0xfffffff8):
        wanted=clean.expected(pointer,8)+clean.expected((pointer+16)&clean.MASK,108)
        for seed in (0,clean.MASK,0x12345678):
            for w,c in product((0,1),repeat=2):
                actual=composed((wo,wn)[w],(wrapper.OFFSET,wrapper.ADDRESS)[w],(wrapper.DELTA,0)[w],(co,cn)[c],(clean.OFFSET,clean.ADDRESS)[c],pointer,seed)
                if actual!=wanted:raise ValueError('composed MMIO mismatch')
                cases+=1
    root=wrapper.ROOT
    return {'cases':cases,'source_admitted':False,'verifier_hashes':{name:hashlib.sha256((root/'tools'/name).read_bytes()).hexdigest() for name in ('verify_gx8002_snpu_task_cmd_cache_flush.py','verify_gx8002_dcache_clean_range.py')},'limits':['Four stock/source combinations; nested stack location and both decoded cache loops. Caller clobbers remain conservative synthetic values; void return ignored. No silicon cache coherence proof.']}
if __name__=='__main__':
    r=verify();(wrapper.ROOT/'docs/research/gx8002-descriptor-cache-composition.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
