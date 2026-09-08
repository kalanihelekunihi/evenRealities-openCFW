#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode OTP-status control flow with modeled volatile reads and helper calls."""
import json,re,struct,subprocess
from build_gx8002_flash_otp_status import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x30001000

def execute(code,pc,delta,flags,manufacturer,status,seed):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)}
    r.update(r0=0x30000000,r14=SP);initial=r.copy();stack={};events=[];flag=False
    reads=[(0x200264f0,0x20028000),(0x20028014,0x20028100),
           (0x20028110,flags),(0x200264f0,0x20028200),(0x20028206,manufacturer)]
    read_index=0;calls=0;result=None
    for _ in range(90):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('push','pop'):
            if args!='r4-r6, r15':raise ValueError('frame register mismatch')
            regs=['r4','r5','r6','r15']
            if op=='push':
                r['r14']-=16
                for i,reg in enumerate(regs):stack[r['r14']+4*i]=r[reg]
            else:
                for i,reg in enumerate(regs):r[reg]=stack[r['r14']+4*i]
                r['r14']+=16
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):
                    raise ValueError('return ABI')
                if read_index!=5:raise ValueError('missing reads')
                return r['r0'],events,result
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','ld.h','ld.hs','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if op=='st.b':
                if a!=0x30000000 or calls!=2:raise ValueError('unexpected output')
                result=r[reg]&255;events.append(['write',a,result])
            else:
                if read_index>=len(reads) or reads[read_index][0]!=a:raise ValueError('unexpected read')
                if (read_index<3 and calls!=0) or (read_index>=3 and calls!=1):raise ValueError('read ordering')
                v=reads[read_index][1];read_index+=1
                r[reg]=(v if op=='ld.w' else v&65535)&MASK
                if op=='ld.hs' and r[reg]&32768:r[reg]|=0xffff0000
                events.append(['read',a,v])
        elif op=='sexth':
            v=r[p[1]]&65535;r[p[0]]=v|0xffff0000 if v&32768 else v
        elif op in ('addi','subi','andi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&b)&MASK
        elif op in ('lsr','asr'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]]&63
            if op=='asr' and a&0x80000000:a-=1<<32
            r[p[0]]=(a>>b)&MASK
        elif op=='cmpnei':flag=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (flag if op=='bt' else not flag):n=int(p[0],0)
        elif op=='bsr':
            target=int(p[0],0)+delta
            if r['r14']!=SP-16:raise ValueError('frame mismatch')
            expected=0x1002375c if calls==0 else 0x10023770
            if calls>1 or target!=expected:raise ValueError('unexpected helper')
            events.append(['call',target]);calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed+0xcafe0000+i)&MASK
            r['r0']=1 if calls==1 else status
        else:raise ValueError('unknown OTP instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=out/'otp-status-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15af4','--stop-address=0x15b38',str(wrapper)],text=True))
    new=decode((out/'otp-status-linked.disassembly.txt').read_text());cases=0
    for flags in (*range(8),0xfffffff8,0xffffffff):
      for manufacturer in (0,0x5e,0x85,0x8000,0xffff):
       for status in (*range(256),*(1<<bit for bit in range(8,32)),0xffffffff,0x7fffffff):
        for seed in (0,0x1234):
         args=(flags,manufacturer,status,seed)
         a=execute(old,0x15af4,0x1000dfec,*args);b=execute(new,0x10023ae0,0,*args)
         expected=0 if manufacturer in (0x5e,0x85) else MASK
         output=(status>>((flags&7)+3))&1 if expected==0 else None
         if a!=b or a[0]!=expected or a[2]!=output:raise ValueError('OTP mismatch')
         cases+=1
    report={'build':evidence,'decoded_cases':cases,'frame_bytes':16,'source_admitted':False,
            'limits':['Helpers modeled; no physical OTP qualification. Rejection tests and admission remain.']}
    (ROOT/'docs/research/gx8002-flash-otp-status-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases);return report
if __name__=='__main__':verify()
