#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare initialization calls, live driver pointer reads and target ABI."""
import json,re,shutil,struct,subprocess
from build_gx8002_npu_regs_init_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x101f6a74
SLOT=0x20027914
CALLS=((0x10205618,1),(0x10205648,2000),(0x10205630,0),(0x10205768,111),(0x1020566c,109),(0x10205660,0x100000))

def expected(pointers):
    trace=[]
    for pointer,(target,arg) in zip(pointers,CALLS):trace.extend([['read',SLOT,pointer],['call',target,pointer,arg]])
    return trace

def execute(code,pc,delta,pointers,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc
    initial=r.copy();saved=None;calls=0;trace=[]
    for _ in range(50):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args!='r4, r15':raise ValueError('NPU initialization frame')
            saved={k:r[k] for k in ('r4','r15')};r['r14']-=8
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('NPU initialization load operand')
            dest,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            if address!=SLOT or calls>=6:raise ValueError('NPU initialization pointer address')
            r[dest]=pointers[calls];trace.append(['read',address,r[dest]])
        elif op=='bsr':
            target=(int(args,0)+delta)&MASK
            if saved is None or r['r14']!=initial['r14']-8:raise ValueError('NPU initialization call frame')
            if target not in {t for t,a in CALLS}:raise ValueError('NPU initialization helper')
            trace.append(['call',target,r['r0'],r['r1']]);calls+=1
            # The pointer slot may change after every helper call. Reads above
            # observe that live value rather than a snapshot at entry.
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4, r15' or r['r14']!=initial['r14']-8:raise ValueError('NPU initialization return frame')
            r.update(saved);r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU initialization ABI')
            return trace
        else:raise ValueError('NPU initialization unknown instruction '+op)
        pc+=width
    raise ValueError('NPU initialization execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-regs-init-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeedc','--stop-address=0xef28',str(w)],text=True));new=decode((out/'npu-regs-init-candidate.disassembly.txt').read_text())
    patterns=[0,MASK,0x10000000,0x20030000,0xa0b00000,*[1<<i for i in range(32)]]
    sequences=[(v,)*6 for v in patterns]
    for index in range(6):
        for value in patterns:
            sequence=[0xa0b00000]*6;sequence[index]=value;sequences.append(tuple(sequence))
    sequences.extend(tuple((seed+i*0x1020304)&MASK for i in range(6)) for seed in patterns)
    cases=0
    for pointers in sequences:
        for seed in (0,MASK,0x12345678):
            wanted=expected(pointers)
            if execute(old,0xeedc,DELTA,pointers,seed)!=wanted or execute(new,0x10205950,0,pointers,seed)!=wanted:raise ValueError('NPU initialization live-pointer/call mismatch')
            cases+=1
    if not evidence['fits']:raise ValueError('NPU initialization envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':0xeedc,'bytes':76,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-regs-init-candidate.elf',output/'npu-regs-init.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Six ordered helper calls with live pointer reloads, exact arguments, caller clobbers and eight-byte frame. Only the external pointer slot is described, not ownership of driver state. Synthetic pointer encodings test forwarding only. Helpers have separate source qualification; no physical MMIO timing claim.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-regs-init-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
