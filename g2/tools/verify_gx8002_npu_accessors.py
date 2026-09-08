#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare NPU accessor calls, decoded primitive MMIO, outputs and ABI."""
import json,re,shutil,struct,subprocess
from build_gx8002_npu_accessor_candidate import ROOT,IMAGE,FUNCTIONS,DELTA,build
from build_gx8002_npu_register_candidate import build as build_registers
from verify_gx8002_npu_registers import execute as execute_register
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
OFFSETS={'npu_get_over_cmd_addr':260,'npu_get_op_overflow_cmd_addr':292,'npu_get_task_head':16,'npu_get_cur_cmd_addr':256}
PRIMITIVES={0x102055ec:'get_value',0x102055f0:'set_value',0x102055cc:'set_bit'}

def setup(name,base,index,value,alias):
    offset=(index<<2)&MASK if name=='npu_get_base_addr' else OFFSETS.get(name,16)
    address=(base+offset)&MASK;output=address if alias else 0x20021000
    memory={output:0xdecafbad,address:value}
    if name=='npu_reset':memory={(base+4)&MASK:value,(base+8)&MASK:value^0x55555555}
    return memory,address,output

def expected(name,base,index,value,alias):
    memory,address,output=setup(name,base,index,value,alias);trace=[]
    if name=='npu_reset':
        for offset in (4,8):
            p=(base+offset)&MASK;old=memory[p];memory[p]=old|8;trace.extend([['call',0x102055cc,p,3],['read',p,old],['write',p,old|8]])
        result=None
    elif name=='npu_set_task_head':
        memory[address]=index;trace=[['call',0x102055f0,address,index],['write',address,index]];result=None
    else:
        result=memory[address];trace=[['call',0x102055ec,address],['read',address,result],['output',output,result]];memory[output]=result
    return trace,memory,result

def execute(code,primitive,pc,delta,name,base,index,value,alias,seed):
    memory,address,output=setup(name,base,index,value,alias);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=base;r['r1']=index if name in ('npu_get_base_addr','npu_set_task_head') else output;r['r2']=output;r['r14']=0x2002f7fc;initial=r.copy();saved=None;frame=0;trace=[]
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args not in ('r15','r4, r15'):raise ValueError('NPU accessor frame')
            regs=(15,) if args=='r15' else (4,15);saved={f'r{i}':r[f'r{i}'] for i in regs};frame=4*len(regs);r['r14']-=frame
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='addi':r[p[0]]=((r[p[0]] if len(p)==2 else r[p[1]])+int(p[-1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('NPU accessor call frame')
            target=(int(args,0)+delta)&MASK
            if target not in PRIMITIVES:raise ValueError('NPU accessor unknown primitive')
            addr=r['r0'];argument=r['r1'];helper=PRIMITIVES[target]
            if addr not in memory:raise ValueError('NPU accessor register address')
            trace.append(['call',target,addr]+([] if helper=='get_value' else [argument]))
            steps,after,result=execute_register(primitive,target-delta,helper,addr,memory[addr],argument,seed);trace.extend(steps);memory[addr]=after
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if result is not None:r['r0']=result
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('NPU accessor output operand')
            reg,b,off=m.groups();addr=(r[b]+int(off,0))&MASK
            if addr!=output or addr&3:raise ValueError('NPU accessor output address/alignment')
            memory[addr]=r[reg];trace.append(['output',addr,r[reg]])
        elif op=='pop':
            wanted='r15' if frame==4 else 'r4, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-frame:raise ValueError('NPU accessor return frame')
            r.update(saved);r['r14']+=frame
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU accessor ABI')
            if frame!=(4 if name=='npu_set_task_head' else 8):raise ValueError('NPU accessor frame size')
            return trace,memory,r['r0'] if name.startswith('npu_get_') else None
        else:raise ValueError('unknown NPU accessor instruction '+op)
        pc+=width
    raise ValueError('NPU accessor execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();registers=build_registers();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-accessor-stock.elf'
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb4c','--stop-address=0xee60',str(w)],text=True));new=decode((out/'npu-accessor-candidate.disassembly.txt').read_text());native=decode((out/'npu-register-native.disassembly.txt').read_text());cases=0
    values=[0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for name,offset,size in FUNCTIONS:
      for base in (0xa0b00000,0x20030000):
       for index in ((0,1,3,64,0x3fffffff,0x40000000,0x80000000,MASK) if name=='npu_get_base_addr' else values if name=='npu_set_task_head' else (0,)):
        for value in values:
         for alias in (False,True):
          for seed in (0,MASK):
           args=(name,base,index,value,alias);wanted=expected(*args)
           if execute(old,old,offset,DELTA,*args,seed)!=wanted or execute(new,native,offset+DELTA,0,*args,seed)!=wanted:raise ValueError('NPU accessor composed trace/state/return mismatch')
           cases+=1
    rows=[];stock=IMAGE.read_bytes()
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('NPU accessor envelope')
        identity=next(f for f in evidence['identification']['functions'] if 'open_cfw_gx8002_'+f['symbol']==region['symbol']);used=identity['object_symbol_size'];offset=region['package_offset'];size=region['stock_envelope_bytes']
        if stock[offset+used:offset+size]!=bytes(size-used):raise ValueError('NPU accessor stock padding')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':offset,'bytes':size,'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-accessor-candidate.elf',output/'npu-accessor.elf')
    return {'functions':rows,'evidence':evidence,'register_source_sha256':registers['source_sha256'],'register_native_sections':registers['regions'],'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Decoded accessor/primitive composition checks ordered calls/MMIO/output stores and observed getter r0 values; original private return types not claimed. Aligned synthetic addresses include output aliasing and 32-bit indexed-address wrap. This is target instruction behavior, not proof arbitrary addresses are valid hardware. Primitive leaf ABI checked separately; full hardware timing unqualified.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-accessor-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
