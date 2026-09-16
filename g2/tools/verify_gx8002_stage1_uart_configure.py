# SPDX-License-Identifier: MIT
"""Compare complete UART setup with modeled arithmetic and readiness."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_uart_configure import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,entry,helpers,baud,retain,frequency,busy,execute_arithmetic=False):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=baud,r1=retain);initial=dict(r);saved=None;pc=entry;trace=[];poll=0;phase=0;condition=False;returns=[]
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r4-r7, r15';saved={k:r[k] for k in ('r4','r5','r6','r7','r15')};r['r14']-=20
        elif op=='pop':
            r.update(saved);r['r14']+=20;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='mult':r[p[0]]=(r[p[0]]*r[p[1]])&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(p[0],0)
        elif op in ('bez','blz'):
            if (r[p[0]]==0 if op=='bez' else bool(r[p[0]]&0x80000000)):nxt=int(p[1],0)
        elif op in ('addu','subu','or'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]
            r[p[0]]=(a+b if op=='addu' else a-b if op=='subu' else a|b)&MASK
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)*(1 if op=='addi' else -1))&MASK
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='rts':
            assert returns;nxt=returns.pop();assert r['r15']==nxt
        elif op=='bnez':
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':
                assert address==0xa010007c;r[reg]=0x80000000|(poll<busy[phase]);poll+=1
                trace.append(['read',address,r[reg]])
            else:
                trace.append(['write',address,r[reg]])
                if address==0xa010000c and r[reg]==128:phase=1;poll=0
        elif op=='bsr':
            target=int(args,0);name=helpers[target]
            if execute_arithmetic and name!='frequency':
                trace.append([name,r['r0'],r['r1']]);returns.append(nxt);r['r15']=nxt;pc=target;continue
            if name=='frequency':assert r['r0']==17;trace.append(['frequency',17]);result=frequency
            else:
                a,b=r['r0'],r['r1'];assert b!=0;trace.append([name,a,b]);result=a//b if name=='divide' else a%b
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('UART polling bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x39bb4','--stop-address=0x39c34',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-stage1-uart-configure/uart.disassembly.txt').read_text())
    helpers={0x38c54:'frequency',0x39774:'divide',0x397b8:'remainder'};mapped={a-0x38954+0x10000000:n for a,n in helpers.items()};cases=0
    for baud,retain,frequency,busy in product((1,9600,115200,0x0fffffff),(0,1,MASK),(0,32768,24000000,MASK),((0,0),(1,3),(4,2))):
        a=execute(old,0x39bb4,helpers,baud,retain,frequency,busy);b=execute(new,0x10001260,mapped,baud,retain,frequency,busy);assert a==b
        writes=[e[1:] for e in b if e[0]=='write'];expected=[[0xa0100004,0],[0xa0100010,3]]
        if not retain:
            denominator=(baud<<4)&MASK;divisor=frequency//denominator;rem=frequency%denominator
            fraction=(((((rem*100)&MASK)//denominator)<<4)&MASK)//100
            expected += [[0xa010000c,128],[0xa0100000,divisor&255],[0xa0100004,(divisor>>8)&255],[0xa01000c0,fraction&255]]
        expected += [[0xa010000c,3],[0xa0100008,79]]
        assert writes==expected;cases+=1
    return {'cases':cases,'build':evidence,'limits':['Complete stock/source UART setup compared with independent register-write oracle and ABI checks. Unsigned division/remainder and frequency modeled, not source closure. Zero shifted denominators and nonterminating hardware polling excluded. Firmware integration pending.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stage1-uart-configure-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'UART setup cases passed')
