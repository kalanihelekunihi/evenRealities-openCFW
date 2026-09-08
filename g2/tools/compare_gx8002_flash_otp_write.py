#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode OTP write against independently ordered effects."""
import json,re,struct,subprocess
from build_gx8002_flash_otp_write import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
from model_gx8002_flash_otp_write import expected,MASK

def execute(code,pc,delta,offset,buffer,length,events,seed=0):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)}
    r.update(r0=offset,r1=buffer,r2=length,r14=0x30001000);initial=r.copy();saved=None;index=0;carry=False
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError(('effect mismatch',e,kind,address,value))
        return e[2]
    for _ in range(500000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r11, r15, r16' or saved is not None:raise ValueError('frame')
            saved={i:r[f'r{i}'] for i in (*range(4,12),15,16)};r['r14']-=40
        elif op=='pop':
            if args!='r4-r11, r15, r16' or saved is None or r['r14']!=initial['r14']-40:raise ValueError('return frame')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=40
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('return ABI/effects')
            return r['r0']
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andi','lsli','addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='andi' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='inct':
            if carry:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('cmpnei','cmphsi','cmphs'):
            b=r[p[1]] if op=='cmphs' else int(p[1],0)
            carry=r[p[0]]!=b if op=='cmpnei' else r[p[0]]>=b
        elif op in ('br','bt','bf','bez','bnez'):
            if op=='br' or op=='bt' and carry or op=='bf' and not carry or op=='bez' and not r[p[0]] or op=='bnez' and r[p[0]]:n=int(p[-1],0)
        elif op in ('ld.w','ld.h','ld.hs','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if op=='st.b':effect('write',address,r[reg]&255)
            else:
                v=effect('read',address);r[reg]=v if op=='ld.w' else v&65535
                if op=='ld.hs' and r[reg]&32768:r[reg]|=0xffff0000
        elif op=='sexth':
            v=r[p[1]]&65535;r[p[0]]=v|0xffff0000 if v&32768 else v
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-40:raise ValueError('call frame')
            target=int(args,0)+delta
            if target not in (0x1002375c,0x1002374c,0x10023b8c,0x10023e14):raise ValueError('unknown helper')
            effect('call',target,[r[f'r{i}'] for i in range(3)] if target in (0x10023b8c,0x10023e14) else [])
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xcafe0000+i+seed)&MASK
        else:raise ValueError('unknown write instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'otp-write-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15ecc','--stop-address=0x15fb8',str(w)],text=True))
    new=decode((out/'otp-write-linked.disassembly.txt').read_text());cases=0
    for offset in (0,1,255,256,511,0xffffffff):
     for length in (0,1,2,255,256,257,513):
      for manufacturer in (0,0x5e,0x85,0xffff):
       for flags in (0,2,7,0xffffffff):
        for seed in (0,0x1234):
         result,events=expected(offset,0xfffffffe,length,1024,4096,4096,flags,manufacturer)
         for code,entry,delta in ((old,0x15ecc,0x1000dfec),(new,0x10023eb8,0)):
            if execute(code,entry,delta,offset,0xfffffffe,length,events,seed)!=result:raise ValueError('write result')
         cases+=1
    overflow_cases=0
    scenarios=[(1,0xffffffff,0,4096,4096,0),
               (255,0xffffff01,0,4096,4096,0),
               (0xffffffff,2,1,0xffffffff,0xffffffff,7),
               (0,513,1024,0xffffffff,0xffffffff,7),
               (255,258,1024,0x80000000,0x80000000,7)]
    for offset,length,size,base,stride,flags in scenarios:
      for seed in (0,0x1234):
        result,events=expected(offset,0xfffffffe,length,size,base,stride,flags,0x85,width=0xffffffff)
        for code,entry,delta in ((old,0x15ecc,0x1000dfec),(new,0x10023eb8,0)):
            if execute(code,entry,delta,offset,0xfffffffe,length,events,seed)!=result:raise ValueError('overflow result')
        overflow_cases+=1
    report={'overflow_cases':overflow_cases,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Modeled helper effects and width changes; broader overflow and rejection tests remain. No physical OTP qualification.']}
    (ROOT/'docs/research/gx8002-flash-otp-write-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
