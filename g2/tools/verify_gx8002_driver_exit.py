#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare reconstructed driver exit call sequences, branches and ABI."""
import json,shutil,struct,subprocess
from build_gx8002_driver_exit_candidate import ROOT,IMAGE,build,FUNCTIONS
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x101f6a74

def execute(code,pc,delta,seed,result):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[];frame=0
    for _ in range(40):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args not in ('r15','r4, r15'):raise ValueError('driver exit frame')
            regs=(15,) if args=='r15' else (4,15);saved={f'r{i}':r[f'r{i}'] for i in regs};frame=len(regs)*4;r['r14']-=frame
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bnez':
            if r[p[0]]!=0:nxt=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('driver exit call frame')
            target=(int(args,0)+delta)&MASK
            if target in (0x100254fc,0x10025504):trace.append(['mask' if target==0x100254fc else 'unmask',r['r0']])
            elif target==0x10205a90:trace.append(['suspend'])
            elif target==0x102055ac:trace.append(['device_exit'])
            elif target==0x10203c88:trace.append(['audio_reset'])
            elif target==0x10025080:trace.append(['gate',r['r0'],r['r1']])
            else:raise ValueError('driver exit unknown helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^(len(trace)*7919)^i)&MASK
            if target==0x10205a90:r['r0']=result&MASK
        elif op=='pop':
            wanted='r15' if frame==4 else 'r4, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-frame:raise ValueError('driver exit return frame')
            r.update(saved);r['r14']+=frame
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('driver exit ABI')
            return trace,r['r0'],frame
        else:raise ValueError('unknown driver exit instruction '+op)
        pc=nxt
    raise ValueError('driver exit execution bound')

def expected(name,result):
    if name=='gx_audio_in_exit':return [['audio_reset'],*([['gate',i,0] for i in (3,2,8,7)])],0,4
    return [['mask',12],['suspend'],['unmask',12]]+([['device_exit']] if result==0 else []),result&MASK,8

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'driver-exit-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    new=decode((out/'driver-exit-candidate.disassembly.txt').read_text());cases=0
    for name,address,offset,size in FUNCTIONS:
        old=decode(subprocess.check_output([pre+'objdump','-D',f'--start-address={offset}',f'--stop-address={offset+size}',str(w)],text=True))
        for seed in (0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678):
            for result in (*range(256),0x7fffffff,0x80000000,0xffffffff,*[1<<i for i in range(8,31)]):
                for code,pc,delta in ((old,offset,DELTA),(new,address,0)):
                    if execute(code,pc,delta,seed,result)!=expected(name,result):raise ValueError('driver exit call/return/frame mismatch')
                cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('driver exit region size')
        rows.append({'symbol':region['symbol'],'section_name':region['section_name'],'compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'driver-exit-candidate.elf',output/'driver-exit.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Helper-call/branch/ABI qualification only. SNPU suspend/device exit, IRQ mask wrappers and audio reset are separate retained functions. Clock gate has independent source qualification. No physical hardware or asynchronous timing qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-driver-exit-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
