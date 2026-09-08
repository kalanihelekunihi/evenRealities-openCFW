#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify OTP erase snapshots, ordering, command reload and wrapped address."""
import json,re,struct,subprocess
from build_gx8002_flash_otp_erase import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x30001000

def execute(code,pc,delta,manufacturer,flags,base,stride,seed):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)};r['r14']=SP
    initial=r.copy();stack={};trace=[];flag=False;calls=0;read_index=0;command=None
    supported=manufacturer in (0x5e,0x85)
    reads=[(0x200264f0,0x20028000),(0x20028006,manufacturer)]
    if supported:reads += [(0x20028014,0x20028100),(0x20028110,flags),(0x20028100,base),(0x20028104,stride)]
    for _ in range(90):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('push','pop'):
            if args!='r4-r7, r15':raise ValueError('frame registers')
            regs=['r4','r5','r6','r7','r15']
            if op=='push':
                r['r14']-=20
                for i,reg in enumerate(regs):stack[r['r14']+i*4]=r[reg]
            else:
                for i,reg in enumerate(regs):r[reg]=stack[r['r14']+i*4]
                r['r14']+=20
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('return ABI')
                if read_index!=len(reads) or calls!=(5 if supported else 0):raise ValueError('missing operations')
                return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','ld.h','ld.hs','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,ptr,offset=m.groups();a=(r[ptr]+int(offset,0))&MASK
            if op=='st.b':
                if a!=0x200264f4 or calls or read_index!=6 or r[reg]!=0x44:raise ValueError('command store')
                command=r[reg];trace.append(['write',a,command])
            elif op=='ld.b':
                if a!=0x200264f4 or calls!=3:raise ValueError('command reload')
                r[reg]=command;trace.append(['read',a,command])
            else:
                if calls or read_index>=len(reads) or reads[read_index][0]!=a:raise ValueError('unexpected read')
                v=reads[read_index][1];read_index+=1;r[reg]=v&MASK
                if op in ('ld.h','ld.hs'):r[reg]&=65535
                if op=='ld.hs' and r[reg]&32768:r[reg]|=0xffff0000
                trace.append(['read',a,v])
        elif op=='sexth':
            v=r[p[1]]&65535;r[p[0]]=v|0xffff0000 if v&32768 else v
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('subi','andi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a&b)&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='cmpnei':flag=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (flag if op=='bt' else not flag):n=int(p[0],0)
        elif op=='bsr':
            sequence=[0x1002375c,0x1002374c,0x10023b8c,0x100236dc,0x1002375c]
            target=int(p[0],0)+delta
            if calls>=5 or target!=sequence[calls]:raise ValueError('helper order')
            if r['r14']!=SP-20:raise ValueError('frame mismatch')
            if command is None:raise ValueError('missing command store')
            args_now=[r[f'r{i}'] for i in range(3)]
            if calls==2:
                if args_now!=[0x200264ec,(base+(flags&7)*stride)&MASK,0x200264f4]:raise ValueError('encode arguments')
                trace.append(['encode',args_now])
                command=(seed^0xa5)&255 # Deliberate helper mutation requires a fresh command-byte read.
            elif calls==3:
                if args_now!=[command,0x200264f5,3]:raise ValueError('write arguments')
                trace.append(['write_command',args_now])
            trace.append(['call',target]);calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed+0xcafe0000+i)&MASK
        else:raise ValueError('unknown erase instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'otp-erase-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15bec','--stop-address=0x15c48',str(wrapper)],text=True))
    new=decode((out/'otp-erase-linked.disassembly.txt').read_text());cases=0
    for manufacturer in (0,0x5e,0x85,0x8000,0xffff):
     for flags in (*range(8),0xfffffff8,0xffffffff):
      for base in (0,4096,0x7fffffff,0xffffffff):
       for stride in (0,1,4096,0x80000000,0xffffffff):
        for seed in (0,0x1234):
         args=(manufacturer,flags,base,stride,seed)
         a=execute(old,0x15bec,0x1000dfec,*args);b=execute(new,0x10023bd8,0,*args)
         if a!=b or a[0]!=0:raise ValueError('erase mismatch')
         cases+=1
    report={'build':evidence,'decoded_cases':cases,'frame_bytes':20,'source_admitted':False,
            'limits':['Helpers modeled with command mutation; physical OTP erase unqualified. Rejection tests and admission pending.']}
    (ROOT/'docs/research/gx8002-flash-otp-erase-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases);return report
if __name__=='__main__':verify()
