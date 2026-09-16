#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""RTC initialization decoded helper/MMIO sequence with finite clock cases."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_rtc_initialize import ROOT,build,Elf32,IMAGE_SHA,sha
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x1000881c


def expected(frequency,control):
    trace=[('gate',0,1),('read',0xa000300c,control),('write',0xa000300c,control|16),('frequency',0)]
    if frequency>=65536:trace.append(('printf',0x10012eb4))
    else:trace.extend([('write',0xa0003020,frequency),('irq',4,0x100087dc,0),('read',0xa000300c,control|16),('write',0xa000300c,control|20)])
    return trace


def execute(code,entry,frequency,control,start_hook=None,gate_hook=None,frequency_hook=None,irq_hook=None,printf_hook=None):
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();saved=None;pc=entry;condition=False;trace=[]
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('RTC init frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('RTC init restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('RTC init ABI')
            return trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('RTC init memory operand')
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if op=='ld.w':
                if a!=0xa000300c:raise ValueError('RTC init read address')
                r[reg]=control;trace.append(('read',a,control))
            else:
                if a not in (0xa000300c,0xa0003020):raise ValueError('RTC init write address')
                trace.append(('write',a,r[reg]))
                if a==0xa000300c:control=r[reg]
        elif op=='bsr':
            target=int(args,0)
            if entry==0x4115c:target=(target+0x10000000-0x38940)&MASK
            value=0xa5216789
            if target==0x10003be8:
                trace.append(('gate',r['r0'],r['r1']))
                if gate_hook is not None:gate_hook(r['r0'],r['r1'])
            elif target==0x10003cf0:
                trace.append(('frequency',r['r0']))
                value=frequency if frequency_hook is None else frequency_hook(r['r0'])
            elif target==0x10009934:
                trace.append(('printf',r['r0']))
                if printf_hook is not None:value=printf_hook(r['r0'])
            elif target==0x10004844:
                trace.append(('irq',r['r0'],r['r1'],r['r2']))
                if irq_hook is not None:irq_hook(r['r0'],r['r1'],r['r2'])
            elif target==0x10008800:
                trace.extend([('read',0xa000300c,control),('write',0xa000300c,control|4)])
                control|=4
                if start_hook is not None:start_hook()
            else:raise ValueError('RTC init helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xa5721368+i*0x113)&MASK
            r['r0']=value
        else:raise ValueError('Unhandled RTC init instruction '+op)
        pc=nxt
    raise ValueError('RTC init execution bound')


def verify():
    candidate=build();out=ROOT/'build/gx8002-board'
    wrapper=Elf32((out/'padmux-get-stock.elf').read_bytes(),'stock')
    assert sha(wrapper.contents(next(s for s in wrapper.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4115c','--stop-address=0x411a8',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-backup-rtc-initialize/device.disassembly.txt').read_text());count=0
    for frequency,control in product((0,1,32768,65534,65535,65536,65537,0x7fffffff,0x80000000,MASK),
                                   (0,MASK,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)])):
        want=expected(frequency,control)
        if execute(old,0x4115c,frequency,control)!=want or execute(new,ADDRESS,frequency,control)!=want:raise ValueError('RTC init decoded mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Helpers modeled by traces, frequency return and caller clobbers; control read represents post-gate state. No helper-body composition, physical RTC or concurrent mutation proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-backup-rtc-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded RTC init cases:',report['decoded_cases'])
