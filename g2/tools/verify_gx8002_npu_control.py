#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify NPU control wrappers composed with decoded register primitives."""
import json,shutil,struct,subprocess
from build_gx8002_npu_control_candidate import ROOT,IMAGE,FUNCTIONS,DELTA,build
from build_gx8002_npu_register_candidate import build as build_registers
from verify_gx8002_npu_registers import execute as execute_register
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
TARGETS={0x102055c0:'get_bit',0x102055cc:'set_bit',0x102055dc:'clear_bit'}

def expected(name,pointer,value):
    address=pointer+12 if name=='all_idle' else pointer;bit=31 if name=='all_idle' else 0
    target=0x102055cc if name=='enable' else 0x102055dc if name=='disable' else 0x102055c0
    trace=[['call',target,address,bit],['read',address,value]]
    if name in ('enable','disable'):
        after=(value|1) if name=='enable' else (value&~1);trace.append(['write',address,after]);result=None
    else:after=value;result=(value>>bit)&1
    return trace,after,result

def execute(code,primitive,pc,delta,name,pointer,value,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=pointer;r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[];after=value
    for _ in range(15):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('NPU control frame')
            saved=r['r15'];r['r14']-=4
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('NPU control call frame')
            target=(int(args,0)+delta)&MASK
            if target not in TARGETS:raise ValueError('NPU control unknown primitive')
            trace.append(['call',target,r['r0'],r['r1']])
            helper_trace,after,result=execute_register(primitive,target-delta,TARGETS[target],r['r0'],value,r['r1'],seed)
            trace.extend(helper_trace)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if result is not None:r['r0']=result
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('NPU control return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU control ABI')
            return trace,after,r['r0'] if name in ('is_enabled','all_idle') else None
        else:raise ValueError('unknown NPU control instruction '+op)
        pc+=width
    raise ValueError('NPU control execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();registers=build_registers();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-control-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb4c','--stop-address=0xec7c',str(w)],text=True));new=decode((out/'npu-control-candidate.disassembly.txt').read_text());native=decode((out/'npu-register-native.disassembly.txt').read_text());cases=0
    values=[0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for name,offset in FUNCTIONS:
      for pointer in (0x10000000,0x20000000,0xa0b00000):
       for value in values:
        for seed in (0,MASK,0x12345678):
         wanted=expected(name,pointer,value)
         if execute(old,old,offset,DELTA,name,pointer,value,seed)!=wanted or execute(new,native,offset+DELTA,0,name,pointer,value,seed)!=wanted:raise ValueError('NPU control composed call/MMIO mismatch')
         cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('NPU control envelope')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':12,'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-control-candidate.elf',output/'npu-control.elf')
    return {'functions':rows,'evidence':evidence,'register_source_sha256':registers['source_sha256'],'register_native_sections':registers['regions'],'cases':cases,'frame_bytes':4,'source_admitted':True,'hardware_qualified':False,'limits':['Decoded wrappers composed with separately ABI-checked leaf register interpreters. Calls conservatively clobber caller-saved registers. Aligned modeled register blocks only; physical MMIO semantics/timing remain unqualified. Full primitive bit-count domain has separate qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-control-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
