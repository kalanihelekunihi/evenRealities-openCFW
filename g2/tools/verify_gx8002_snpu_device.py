#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify original empty hooks and SNPU IRQ forwarding, without stub claims."""
import json, shutil, subprocess
from build_gx8002_snpu_device_candidate import ROOT, IMAGE, FUNCTIONS, DELTA, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff

def execute(code,pc,delta,name,handler,data,seed):
    registers={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    registers.update(r0=handler,r1=data,r14=0x2002f7fc)
    initial=registers.copy();saved=None;trace=[]
    for _ in range(12):
        op,args,width=code[pc];parts=[p.strip() for p in args.split(',')]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('SNPU shim frame')
            saved=registers['r15'];registers['r14']-=4
        elif op=='mov':registers[parts[0]]=registers[parts[1]]
        elif op=='movi':registers[parts[0]]=int(parts[1],0)
        elif op=='bsr':
            target=(int(args,0)+delta)&MASK
            if target!=0x1002553c:raise ValueError('SNPU shim unknown helper')
            if saved is None or registers['r14']!=initial['r14']-4:raise ValueError('SNPU shim call frame')
            trace.append([target,registers['r0'],registers['r1'],registers['r2']])
            for i in (0,1,2,3,12,13,15,*range(18,32)):registers[f'r{i}']=(seed^0xcafe0000^i)&MASK
        elif op=='pop':
            if args!='r15' or saved is None or registers['r14']!=initial['r14']-4:raise ValueError('SNPU shim return frame')
            registers['r15']=saved;registers['r14']+=4
            if name!='snpu_request_irq':raise ValueError('SNPU empty hook gained a frame')
            if any(registers[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SNPU shim ABI')
            return trace
        elif op=='rts':
            if name=='snpu_request_irq' or saved is not None or registers!=initial or trace:raise ValueError('SNPU empty hook changed state')
            return trace
        else:raise ValueError('SNPU shim unknown instruction '+op)
        pc+=width
    raise ValueError('SNPU shim execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb34','--stop-address=0xeb4c',str(out/'snpu-device-stock.elf')],text=True))
    new=decode((out/'snpu-device-candidate.disassembly.txt').read_text());cases=0
    # Encodings are forwarded, not called as callbacks in this shim. Null and
    # odd encodings test transport only; they are not declared valid handlers.
    patterns=[0,MASK,0x10026000,0x20020000,*[1<<i for i in range(32)]]
    for name,offset,size in FUNCTIONS:
        for handler in patterns:
            for data in patterns:
                for seed in (0,MASK,0x12345678):
                    expected=[[0x1002553c,12,handler,data]] if name=='snpu_request_irq' else []
                    if execute(old,offset,DELTA,name,handler,data,seed)!=expected or execute(new,offset+DELTA,0,name,handler,data,seed)!=expected:raise ValueError('SNPU shim call/argument mismatch')
                    cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('SNPU shim envelope')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-device-candidate.elf',output/'snpu-device.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Empty init/exit match authenticated original returns with all modeled registers unchanged. Request wrapper forwards fixed IRQ 12 and pointer bits, conservatively clobbers caller registers at the separately qualified IRQ helper, and restores its four-byte frame. Pointer encodings are transport cases, not proof of valid callable addresses. No hardware timing qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-device-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
