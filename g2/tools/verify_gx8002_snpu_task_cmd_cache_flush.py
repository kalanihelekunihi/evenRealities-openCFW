#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify descriptor cache publication call order and ABI, not cache hardware."""
import json,shutil,struct,subprocess
from build_gx8002_snpu_task_cmd_cache_flush_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
OFFSET=0xef74
ADDRESS=0x102059e8
DELTA=0x101f6a74
TARGET=0x10025664

def execute(code,pc,delta,pointer,seed,clean_call=None,stack_top=0x2002f7fc):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    r['r0']=pointer;r['r14']=stack_top;initial=r.copy();saved=None;calls=[]
    for _ in range(16):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if saved is not None or args!='r4, r15':raise ValueError('cache wrapper frame')
            saved={k:r[k] for k in ('r4','r15')};r['r14']-=8
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)&MASK
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='bsr':
            target=(int(args,0)+delta)&MASK
            if target!=TARGET or saved is None or r['r14']!=initial['r14']-8:raise ValueError('cache wrapper call target/frame')
            calls.append((target,r['r0'],r['r1']))
            if clean_call is not None:clean_call(r['r0'],r['r1'],r['r14'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^len(calls)*0x1234567^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4, r15' or r['r14']!=initial['r14']-8:raise ValueError('cache wrapper return frame')
            r.update(saved);r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('cache wrapper ABI')
            return calls,r['r0']
        else:raise ValueError('cache wrapper unknown instruction '+op)
        pc+=width
    raise ValueError('cache wrapper bound')

def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-task-cmd-cache-flush-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xef74','--stop-address=0xef8c',str(w)],text=True))
    return old,decode((out/'snpu-task-cmd-cache-flush-candidate.disassembly.txt').read_text())

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();old,new=programs();cases=0
    pointers=(0,1,0x20027360,0x20027870,0xfffffff0,0xfffffff1,MASK,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)])
    for pointer in pointers:
        for seed in (0,MASK,0x12345678,*[1<<i for i in range(32)]):
            wanted=([(TARGET,pointer,8),(TARGET,(pointer+16)&MASK,108)],(seed^0xcafe0000^2*0x1234567)&MASK)
            if execute(old,OFFSET,DELTA,pointer,seed)!=wanted or execute(new,ADDRESS,0,pointer,seed)!=wanted:raise ValueError('cache wrapper call/return mismatch')
            cases+=1
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':24,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if not evidence['fits']:raise ValueError('cache wrapper envelope')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/snpu-task-cmd-cache-flush-candidate.elf',output/'snpu-task-cmd-cache-flush.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Wrapper-only call order, 32-bit pointer arithmetic, conservative caller clobbers and eight-byte frame. Synthetic wrapping arguments do not establish physical address validity or cache coherence. Cache implementation requires separate qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-task-cmd-cache-flush-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
