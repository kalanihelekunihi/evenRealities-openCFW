#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check a receive-loop iteration under the explicit nonempty-loop precondition."""
import json,re,subprocess
from compare_gx8002_flash_otp_read import ROOT,decode,MASK

def step(code,start,exit_pc,cursor_reg,end_reg,cursor,end,word,delay):
    if cursor==end:raise ValueError('nonempty precondition')
    r={f'r{i}':0x12340000+i for i in range(32)}
    r.update(r4=0xa2000000);r[cursor_reg]=cursor;r[end_reg]=end
    initial=r.copy();pc=start;trace=[];polls=0;writes=0;carry=False
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();a=r[base]+int(off,0)
            if a==0xa2000028:v=0 if polls<delay else 8;polls+=1
            elif a==0xa2000060:v=word
            else:raise ValueError('unexpected read')
            trace.append(['read',a,v]);r[reg]=v
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='bez':
            if not r[p[0]]:n=int(p[1],0)
        elif op=='stbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);reg,base=m.groups()
            trace.append(['write',r[base],r[reg]&255]);r[base]=(r[base]+1)&MASK;writes+=1
        elif op=='cmpne':carry=r[p[0]]!=r[p[1]]
        elif op in ('br','bt'):
            if op=='br' or carry:n=int(p[0],0)
        else:raise ValueError('unexpected loop instruction '+op)
        if writes and n in (start,exit_pc):
            allowed={cursor_reg,'r1','r2'} if cursor_reg=='r9' else {cursor_reg,'r2'}
            if any(r[k]!=v for k,v in initial.items() if k not in allowed):raise ValueError('loop clobber')
            return r[cursor_reg],n==exit_pc,trace
        pc=n
    raise ValueError('loop bound')

def check_structure(code,source):
    # Exact decoded operations tie the arithmetic argument to actual code.
    rows = [
        (0x10024084,'ld.w','r1, (r4, 0x28)',2),
        (0x10024086,'andi','r2, r1, 8',4),
        (0x1002408a,'bez','r2, 0x10024084',4),
        (0x1002408e,'ld.w','r2, (r4, 0x60)',2),
        (0x10024090,'stbi.b','r2, (r9)',4),
        (0x10024094,'cmpne','r3, r9',2),
        (0x10024096,'bt','0x10024084',2),
    ] if source else [
        (0x160f2,'ld.w','r2, (r4, 0x28)',2),
        (0x160f4,'andi','r2, r2, 8',4),
        (0x160f8,'bez','r2, 0x160f2',4),
        (0x160fc,'ld.w','r2, (r4, 0x60)',2),
        (0x160fe,'stbi.b','r2, (r3)',4),
        (0x16102,'br','0x1609c',2),
        (0x1609c,'cmpne','r1, r3',2),
        (0x1609e,'bt','0x160f2',2),
    ]
    for pc,op,args,width in rows:
        if code.get(pc)!=(op,args,width):raise ValueError('receive-loop structure changed')
    return len(rows)

def verify():
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x1609c','--stop-address=0x16104',str(out/'otp-read-stock.elf')],text=True))
    new=decode((out/'otp-read-linked.disassembly.txt').read_text());cases=0
    structure=[check_structure(old,False),check_structure(new,True)]
    for cursor in (0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff):
     for distance in (1,2,31,32,0x7fffffff,0x80000000,0xffffffff):
      end=(cursor+distance)&MASK
      for word in (0,0x12345678,0xffffffff):
       for delay in (0,2):
        a=step(old,0x160f2,0x160a0,'r3','r1',cursor,end,word,delay)
        b=step(new,0x10024084,0x10024098,'r9','r3',cursor,end,word,delay)
        trace=[['read',0xa2000028,0]]*delay+[['read',0xa2000028,8],['read',0xa2000060,word],['write',cursor,word&255]]
        reference=((cursor+1)&MASK,distance==1,trace)
        if a!=reference or b!=reference:raise ValueError('receive step mismatch')
        cases+=1
    report={'checked_instruction_counts':structure,'cases':cases,'precondition':'cursor != end; readiness eventually asserted',
            'step':'read one FIFO word, store low byte, cursor=(cursor+1) mod 2^32, exit iff cursor=end',
            'limits':['One-iteration decoded checks, not full huge-transfer or hardware qualification. Entry/cleanup and integration with an induction argument remain.']}
    (ROOT/'docs/research/gx8002-otp-receive-step-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
