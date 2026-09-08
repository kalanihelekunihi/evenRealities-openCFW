#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare NPU interrupt mask calls, decoded primitive MMIO, outputs and ABI."""
import json,re,shutil,struct,subprocess
from build_gx8002_npu_interrupt_mask_candidate import ROOT,IMAGE,FUNCTIONS,DELTA,build
from build_gx8002_npu_register_candidate import build as build_registers
from verify_gx8002_npu_registers import execute as execute_register
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
PRIMITIVES={0x102055ec:'get_value',0x102055f0:'set_value',0x102055cc:'set_bit',0x102055dc:'clear_bit'}

def setup(name,base,index,value,alias):
    address=base+(4 if name=='npu_en_interrupt' else 8)
    return {address:value},address,None

def observed_read(value, ordinal, mode):
    # A changing device can return a fresh value at every RMW; writes need
    # not be reflected by subsequent reads. This is a trace model only.
    return (value ^ ((ordinal * 0x9e3779b9)&MASK)) if mode else value

def expected(name,base,index,value,alias):
    memory,address,_=setup(name,base,index,value,alias);trace=[];ordinal=0
    flags=(1,2,4,8,16,32,64);bits=(0,4,8,12,13,14,16)
    for flag,bit in zip(flags,bits):
        if name=='npu_clr_interrupt_without_overflow' and flag in (16,32):continue
        if name=='npu_clr_overflow_interrupt' and flag not in (16,32):continue
        if not index&flag:continue
        old=observed_read(value,ordinal,True) if alias else memory[address]
        after=old|(1<<bit);ordinal+=1
        trace.extend([['call',0x102055cc,address,bit],['read',address,old],['write',address,after]])
        memory[address]=after
    return trace,memory,None

def execute(code,primitive,pc,delta,name,base,index,value,alias,seed):
    memory,address,output=setup(name,base,index,value,alias);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=base;r['r1']=index;r['r2']=output;r['r14']=0x2002f7fc;initial=r.copy();saved=None;frame=0;trace=[]
    ordinal=0
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args not in ('r15','r4-r5, r15'):raise ValueError('NPU interrupt mask frame')
            regs=(15,) if args=='r15' else (4,5,15);saved={f'r{i}':r[f'r{i}'] for i in regs};frame=4*len(regs);r['r14']-=frame
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='addi':r[p[0]]=((r[p[0]] if len(p)==2 else r[p[1]])+int(p[-1],0))&MASK
        elif op=='addu':r[p[0]]=((r[p[0]]+r[p[1]]) if len(p)==2 else (r[p[1]]+r[p[2]]))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&0xffff
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):pc=int(p[1],0);continue
        elif op=='br':pc=int(args,0);continue
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('NPU interrupt mask call frame')
            target=(int(args,0)+delta)&MASK
            if target not in PRIMITIVES:raise ValueError('NPU interrupt mask unknown primitive')
            addr=r['r0'];argument=r['r1'];helper=PRIMITIVES[target]
            if addr not in memory:raise ValueError('NPU interrupt mask register address')
            trace.append(['call',target,addr]+([] if helper=='get_value' else [argument]))
            old=observed_read(value,ordinal,True) if alias else memory[addr];ordinal+=1
            steps,after,result=execute_register(primitive,target-delta,helper,addr,old,argument,seed);trace.extend(steps);memory[addr]=after
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if result is not None:r['r0']=result
        elif op=='pop':
            wanted='r15' if frame==4 else 'r4-r5, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-frame:raise ValueError('NPU interrupt mask return frame')
            r.update(saved);r['r14']+=frame
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU interrupt mask ABI')
            if frame!=12:raise ValueError('NPU interrupt mask frame size')
            return trace,memory,None
        else:raise ValueError('unknown NPU interrupt mask instruction '+op)
        pc+=width
    raise ValueError('NPU interrupt mask execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();registers=build_registers();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-interrupt-stock.elf'
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb4c','--stop-address=0xee60',str(w)],text=True));new=decode((out/'npu-interrupt-mask-candidate.disassembly.txt').read_text());native=decode((out/'npu-register-native.disassembly.txt').read_text());cases=0
    values=[0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for name,offset,size in FUNCTIONS:
      for base in (0xa0b00000,0x20030000):
       for index in [low|high for low in range(128) for high in (0,0xffffff80,0x80000000)]:
        for value in (0,MASK,0x12345678):
         for seed,mode in ((0,False),(MASK,False),(0,True),(MASK,True)):
           args=(name,base,index,value,mode);wanted=expected(*args)
           if execute(old,old,offset,DELTA,*args,seed)!=wanted or execute(new,native,offset+DELTA,0,*args,seed)!=wanted:raise ValueError('NPU interrupt mask composed trace/state mismatch')
           cases+=1
    rows=[];stock=IMAGE.read_bytes()
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('NPU interrupt mask envelope')
        identity=next(f for f in evidence['identification']['functions'] if 'open_cfw_gx8002_'+f['symbol']==region['symbol']);used=identity['object_symbol_size'];offset=region['package_offset'];size=region['stock_envelope_bytes']
        if stock[offset+used:offset+size]!=bytes(size-used):raise ValueError('NPU interrupt mask stock padding')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':offset,'bytes':size,'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-interrupt-mask-candidate.elf',output/'npu-interrupt-mask.elf')
    return {'functions':rows,'evidence':evidence,'register_source_sha256':registers['source_sha256'],'register_native_sections':registers['regions'],'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Decoded mask/primitive composition checks every low-seven-bit flag combination with ignored high bits, ordered individual RMW operations, latched and changing read values, caller clobbers and 12-byte frames. Aligned synthetic addresses only; physical interrupt register semantics and timing remain unqualified.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-interrupt-mask-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
