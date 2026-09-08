#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare NPU interrupt status calls, decoded primitive MMIO, outputs and ABI."""
import json,re,shutil,struct,subprocess
from build_gx8002_npu_interrupt_status_candidate import ROOT,IMAGE,FUNCTIONS,DELTA,build
from build_gx8002_npu_register_candidate import build as build_registers
from verify_gx8002_npu_registers import execute as execute_register
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
PRIMITIVES={0x102055ec:'get_value'}

def setup(name,base,index,value,alias):
    address=base+12;output=address if alias else 0x20021000
    return {output:0xdecafbad,address:value},address,output

def expected(name,base,index,value,alias):
    memory,address,output=setup(name,base,index,value,alias)
    trace=[['call',0x102055ec,address],['read',address,value]]
    result=(value&1)|(2 if value&16 else 0)
    memory[output]=result;trace.append(['output',output,result]);ordinal=0
    for bit,flag in ((8,4),(12,8),(13,16),(14,32),(16,64)):
        if not value&(1<<bit):continue
        old=(index^((ordinal*0x9e3779b9)&MASK)) if index else memory[output]
        ordinal+=1;trace.append(['output_read',output,old]);result=old|flag
        memory[output]=result;trace.append(['output',output,result])
    return trace,memory,value&0x10000

def execute(code,primitive,pc,delta,name,base,index,value,alias,seed):
    memory,address,output=setup(name,base,index,value,alias);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=base;r['r1']=output;r['r2']=output;r['r14']=0x2002f7fc;initial=r.copy();saved=None;frame=0;trace=[]
    ordinal=0
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args not in ('r15','r4, r15'):raise ValueError('NPU interrupt status frame')
            regs=(15,) if args=='r15' else (4,15);saved={f'r{i}':r[f'r{i}'] for i in regs};frame=4*len(regs);r['r14']-=frame
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='addi':r[p[0]]=((r[p[0]] if len(p)==2 else r[p[1]])+int(p[-1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):pc=int(p[1],0);continue
        elif op=='br':pc=int(args,0);continue
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('NPU interrupt status call frame')
            target=(int(args,0)+delta)&MASK
            if target not in PRIMITIVES:raise ValueError('NPU interrupt status unknown primitive')
            addr=r['r0'];argument=r['r1'];helper=PRIMITIVES[target]
            if addr not in memory:raise ValueError('NPU interrupt status register address')
            trace.append(['call',target,addr]+([] if helper=='get_value' else [argument]))
            steps,after,result=execute_register(primitive,target-delta,helper,addr,memory[addr],argument,seed);trace.extend(steps);memory[addr]=after
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if result is not None:r['r0']=result
        elif op in ('st.w','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('NPU interrupt status output operand')
            reg,b,off=m.groups();addr=(r[b]+int(off,0))&MASK
            if addr!=output or addr&3:raise ValueError('NPU interrupt status output address/alignment')
            if op=='st.w':memory[addr]=r[reg];trace.append(['output',addr,r[reg]])
            else:
                r[reg]=(index^((ordinal*0x9e3779b9)&MASK)) if index else memory[addr]
                ordinal+=1;trace.append(['output_read',addr,r[reg]])
        elif op=='pop':
            wanted='r15' if frame==4 else 'r4, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-frame:raise ValueError('NPU interrupt status return frame')
            r.update(saved);r['r14']+=frame
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU interrupt status ABI')
            if frame!=8:raise ValueError('NPU interrupt status frame size')
            return trace,memory,r['r0'] if name.startswith('npu_get_') else None
        else:raise ValueError('unknown NPU interrupt status instruction '+op)
        pc+=width
    raise ValueError('NPU interrupt status execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();registers=build_registers();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-interrupt-stock.elf'
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb4c','--stop-address=0xee60',str(w)],text=True));new=decode((out/'npu-interrupt-status-candidate.disassembly.txt').read_text());native=decode((out/'npu-register-native.disassembly.txt').read_text());cases=0
    relevant=(0,4,8,12,13,14,16);bitmask=sum(1<<b for b in relevant)
    values=[sum((1<<bit) for i,bit in enumerate(relevant) if combo&(1<<i))|ignored for combo in range(128) for ignored in (0,MASK^bitmask)]
    for name,offset,size in FUNCTIONS:
      for base in (0xa0b00000,0x20030000):
       for index in (0,0x12345678,MASK):
        for value in values:
         for alias in (False,True):
          for seed in (0,MASK):
           args=(name,base,index,value,alias);wanted=expected(*args)
           if execute(old,old,offset,DELTA,*args,seed)!=wanted or execute(new,native,offset+DELTA,0,*args,seed)!=wanted:raise ValueError('NPU interrupt status trace/state/return mismatch')
           cases+=1
    rows=[];stock=IMAGE.read_bytes()
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('NPU interrupt status envelope')
        identity=next(f for f in evidence['identification']['functions'] if 'open_cfw_gx8002_'+f['symbol']==region['symbol']);used=identity['object_symbol_size'];offset=region['package_offset'];size=region['stock_envelope_bytes']
        if stock[offset+used:offset+size]!=bytes(size-used):raise ValueError('NPU interrupt status stock padding')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':offset,'bytes':size,'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-interrupt-status-candidate.elf',output/'npu-interrupt-status.elf')
    return {'functions':rows,'evidence':evidence,'register_source_sha256':registers['source_sha256'],'register_native_sections':registers['regions'],'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Decoded status/primitive composition checks one snapshot register read, separate volatile output updates, observed r0, helper clobbers and eight-byte frame. Every relevant-bit combination with ignored bits, aliasing and changing output reads modeled. Original private return type and physical MMIO semantics remain unqualified.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-interrupt-status-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
