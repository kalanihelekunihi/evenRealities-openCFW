#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify public IRQ wrapper target, argument bits and frame preservation."""
import json,shutil,struct,subprocess
from build_gx8002_irq_mask_candidate import ROOT,IMAGE,build,FUNCTIONS
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x1000dfec

def execute(code,pc,delta,irq,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=irq;r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[]
    for _ in range(8):
        op,args,width=code[pc]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('IRQ wrapper frame')
            saved=r['r15'];r['r14']-=4
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('IRQ wrapper call frame')
            target=(int(args,0)+delta)&MASK
            if target not in (0x100254ac,0x100254c8):raise ValueError('IRQ wrapper unknown helper')
            trace.append([target,r['r0']])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('IRQ wrapper return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('IRQ wrapper ABI')
            return trace
        else:raise ValueError('unknown IRQ wrapper instruction '+op)
        pc+=width
    raise ValueError('IRQ wrapper execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'irq-mask-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x17510','--stop-address=0x17520',str(w)],text=True));new=decode((out/'irq-mask-candidate.disassembly.txt').read_text());cases=0
    for name,address,offset in FUNCTIONS:
        target=0x100254c8 if name=='gx_mask_irq' else 0x100254ac
        for irq in (*range(256),0x7fffffff,0x80000000,MASK,*[1<<i for i in range(8,31)],*[MASK^(1<<i) for i in range(32)]):
            for seed in (0,MASK,0x12345678):
                for code,pc,delta in ((old,offset,DELTA),(new,address,0)):
                    if execute(code,pc,delta,irq,seed)!=[[target,irq]]:raise ValueError('IRQ wrapper call/argument mismatch')
                cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits'] or not region['exact_stock_payload']:raise ValueError('IRQ wrapper region')
        rows.append({'symbol':region['symbol'],'section_name':region['section_name'],'compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':8,'sha256':region['stock_sha256'],'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'irq-mask-candidate.elf',output/'irq-mask.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':4,'source_admitted':True,'hardware_qualified':False,'limits':['Wrapper call/argument-bit/ABI comparison only. Internal signed IRQ implementation has separate source qualification; this does not expand its valid IRQ domain or prove physical interrupt timing.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-irq-mask-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
