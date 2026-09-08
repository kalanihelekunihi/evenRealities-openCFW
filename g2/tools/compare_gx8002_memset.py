#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode byte/word stores and signed loop boundaries in stock/source memset."""
import json,re,struct,subprocess
from build_gx8002_memset_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def signed(n):return n if n<0x80000000 else n-0x100000000

def execute(code,pc,destination,value,count,seed=0,prefix=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=destination;r['r1']=value;r['r2']=count;r['r14']=0x2002f7fc
    initial=r.copy();trace=[];condition=False
    for _ in range(200000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='mov':r[p[0]]=r[p[1]]
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op in ('or','addu'):
            a,b=(r[p[0]],r[p[1]]) if len(p)==2 else (r[p[1]],r[p[2]])
            r[p[0]]=(a|b) if op=='or' else (a+b)&MASK
        elif op in ('addi','subi'):
            a,b=(r[p[0]],int(p[1],0)) if len(p)==2 else (r[p[1]],int(p[2],0))
            r[p[0]]=(a+b if op=='addi' else a-b)&MASK
        elif op=='cmplti':condition=signed(r[p[0]])<int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op in ('st.b','st.w','stbi.w'):
            pattern=r'(r\d+), \((r\d+)\)' if op=='stbi.w' else r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)'
            m=re.fullmatch(pattern,args)
            if not m:raise ValueError('memset store operand')
            reg,base=m.group(1,2);offset=0 if op=='stbi.w' else int(m.group(3),0);address=(r[base]+offset)&MASK;size=1 if op=='st.b' else 4
            if size==4 and address&3:raise ValueError('unaligned memset word')
            if prefix is not None and len(trace)==prefix:return {'trace':trace,'checkpoint':True}
            trace.append([address,size,r[reg]&(255 if size==1 else MASK)])
            if op=='stbi.w':r[base]=(r[base]+4)&MASK
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('memset ABI')
            return {'trace':trace,'result':r['r0']}
        else:raise ValueError('unknown memset instruction '+op)
        pc=nxt
    raise ValueError('memset execution bound')

def expected(destination,value,count,prefix=None):
    cursor=destination;remaining=count;trace=[];byte=value&255;word=byte*0x01010101
    def store(size):
        nonlocal cursor
        if prefix is not None and len(trace)==prefix:return False
        trace.append([cursor,size,byte if size==1 else word]);cursor=(cursor+size)&MASK;return True
    if remaining:
        while cursor&3:
            if not store(1):return {'trace':trace,'checkpoint':True}
            remaining=(remaining-1)&MASK
            if remaining==0:return {'trace':trace,'result':destination}
        while signed(remaining)>=16:
            for _ in range(4):
                if not store(4):return {'trace':trace,'checkpoint':True}
            remaining-=16
        while signed(remaining)>=4:
            if not store(4):return {'trace':trace,'checkpoint':True}
            remaining-=4
        # Stock's explicit tail is bounded to three stores even for negative
        # signed block counts. Do not silently substitute an unsigned loop.
        for _ in range(3):
            if remaining==0:break
            if not store(1):return {'trace':trace,'checkpoint':True}
            remaining=(remaining-1)&MASK
    return {'trace':trace,'result':destination}

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'memset-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x12f58','--stop-address=0x12ff8',str(w)],text=True));new=decode((out/'memset-candidate.disassembly.txt').read_text());cases=0;prefixes=0
    def check(address,value,count,seed,prefix=None):
        want=expected(address,value,count,prefix)
        for code,pc in ((old,0x12f58),(new,0x102099cc)):
            if execute(code,pc,address,value,count,seed,prefix)!=want:raise ValueError('memset trace mismatch')
    for alignment in range(4):
     for count in (*range(36),63,64,65,160,164,255,256,257):
      for byte in range(256):
       check(0x20010000+alignment,0xdead0000|byte,count,byte);cases+=1
    for address in (0x20010000,0x20010001,0x20010002,0x20010003):
     for count in (1024,4095,4096,4097,25536,65536):
      for value in (0,0xffffffff,0x12345678):check(address,value,count,value);cases+=1
    for address in (0,1,2,3,0xfffffffc,0xfffffffd,0xfffffffe,0xffffffff):
     for count in (0,1,2,3,4,15,16,17,0x80000003,0x80000004,0xfffffffe,0xffffffff):
      check(address,0xffffffff,count,0xffffffff);cases+=1
     for count in (0x7fffffff,0x80000000,0x80000001,0x80000002):
      check(address,0x12345678,count,0xabcdef,32);prefixes+=1
    report={'build':evidence,'cases':cases,'large_count_prefix_cases':prefixes,'frame_bytes':0,'source_admitted':False,
      'limits':['Decoded ordered byte/word traces, normal lengths and wraparound arithmetic. Huge positive loop paths use32-store checkpoints, not full execution or valid-memory claims. No hardware/MMIO/timing qualification; arbitrary addresses in arithmetic cases are synthetic.']}
    (ROOT/'docs/research/gx8002-memset-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
