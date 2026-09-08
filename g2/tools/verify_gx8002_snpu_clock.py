#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check save/MMIO/restore ordering and exact saved-state propagation."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_clock_candidate import ROOT,IMAGE,ADDRESS,OFFSET,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x1000dfec
GATE=0xa0300018

def expected(enable,value,state):return [['save',state],['read',GATE,value],['write',GATE,(value&~0x100) if enable else (value|0x100)],['restore',state]]

def execute(code,pc,delta,enable,value,state,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=enable;r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[]
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r4, r15':raise ValueError('SNPU clock frame')
            saved={'r4':r['r4'],'r15':r['r15']};r['r14']-=8
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movih':r[p[0]]=(int(p[1],0)<<16)&MASK
        elif op=='bclri':r[p[0]]&=MASK^(1<<int(p[1],0))
        elif op=='andni':r[p[0]]=r[p[1]]&(MASK^int(p[2],0))
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('SNPU clock memory operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if address!=GATE:raise ValueError('SNPU clock register address')
            if op=='ld.w':r[reg]=value;trace.append(['read',address,value])
            else:trace.append(['write',address,r[reg]])
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-8:raise ValueError('SNPU clock call frame')
            target=(int(args,0)+delta)&MASK
            if target==0x10025560:trace.append(['save',state])
            elif target==0x1002556c:trace.append(['restore',r['r0']])
            else:raise ValueError('SNPU clock unknown helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if target==0x10025560:r['r0']=state
        elif op=='pop':
            if saved is None or args!='r4, r15' or r['r14']!=initial['r14']-8:raise ValueError('SNPU clock return frame')
            r.update(saved);r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SNPU clock ABI')
            return trace
        else:raise ValueError('unknown SNPU clock instruction '+op)
        pc=nxt
    raise ValueError('SNPU clock execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-clock-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x17200','--stop-address=0x17224',str(w)],text=True));new=decode((out/'snpu-clock-candidate.disassembly.txt').read_text());cases=0
    values=[0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for enable in (0,1,2,0x7fffffff,0x80000000,MASK):
      for value in values:
       for state in (0,0x40,0x100,0x140,0x80000200,MASK,0x12345678):
        for seed in (0,MASK,0x12345678):
         wanted=expected(enable,value,state)
         for code,pc,delta in ((old,OFFSET,DELTA),(new,ADDRESS,0)):
          if execute(code,pc,delta,enable,value,state,seed)!=wanted:raise ValueError('SNPU clock ordering/value mismatch')
         cases+=1
    if not evidence['fits']:raise ValueError('SNPU clock envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':36,'sha256':evidence['stock_sha256'],'region':'image_a_sram_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-clock-candidate.elf',output/'snpu-clock.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'frame_bytes':8,'source_admitted':True,'hardware_qualified':False,'limits':['Decoded call/MMIO/ABI comparison. Saved-state patterns are helper return contracts, not claims that all patterns are valid physical PSR states. IRQ save/restore independently source-qualified. No hardware clock or interrupt timing proof.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-clock-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
