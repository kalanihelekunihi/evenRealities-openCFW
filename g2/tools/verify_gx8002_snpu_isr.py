#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify the state-gated ISR and observed return register."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_isr_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
ADDRESS=0x10205ce0
OFFSET=0xf26c
DELTA=0x101f6a74
STATE=0x20027350
HELPER=0x10205bd8

def expected(state,result):return ([['read',STATE,state]]+([['call',HELPER]] if state!=2 else []),result if state!=2 else 2)

def execute(code,pc,delta,state,result,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;condition=False;trace=[]
    for _ in range(15):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('SNPU ISR frame')
            saved=r['r15'];r['r14']-=4
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('SNPU ISR load operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if address!=STATE:raise ValueError('SNPU ISR state address')
            r[reg]=state;trace.append(['read',address,state])
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('SNPU ISR call frame')
            if ((int(args,0)+delta)&MASK)!=HELPER:raise ValueError('SNPU ISR helper')
            trace.append(['call',HELPER])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            r['r0']=result
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('SNPU ISR return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SNPU ISR ABI')
            return trace,r['r0']
        else:raise ValueError('SNPU ISR unknown instruction '+op)
        pc=nxt
    raise ValueError('SNPU ISR execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-isr-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf26c','--stop-address=0xf280',str(w)],text=True));new=decode((out/'snpu-isr-candidate.disassembly.txt').read_text());cases=0
    patterns=[0,1,2,3,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for state in patterns:
        for result in patterns:
            for seed in (0,MASK,0x12345678):
                wanted=expected(state,result)
                if execute(old,OFFSET,DELTA,state,result,seed)!=wanted or execute(new,ADDRESS,0,state,result,seed)!=wanted:raise ValueError('SNPU ISR state/call/return mismatch')
                cases+=1
    if not evidence['fits']:raise ValueError('SNPU ISR envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':20,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-isr-candidate.elf',output/'snpu-isr.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['State-gated call boundary and observed r0 only; original private return types are inferred. Preserves state2 return and arbitrary helper result, caller clobbers and four-byte frame. process_status remains separately unrecovered. No physical interrupt timing qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-isr-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
