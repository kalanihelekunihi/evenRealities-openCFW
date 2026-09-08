#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded RTC callback/acknowledgement ordering and ABI contract."""
import hashlib,json,re,shutil,subprocess
from verify_gx8002_logging import check_paths
from analyze_gx8002_rtc_primitives import analyze
from itertools import product
from build_gx8002_rtc_isr_candidate import ROOT,build
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x10206680


def expected(irq,callback,argument,result,ack):
    trace=[('read',0x20027b40,callback)]
    if callback:trace.extend([('read',0x20027b44,argument),('call',callback,irq,argument)])
    trace.append(('read',0xa0003018,ack))
    return trace,result if callback else 0


def execute(code,entry,irq,callback,argument,result,ack):
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=irq,r14=0x2002f7fc);initial=r.copy();saved=None;pc=entry;trace=[]
    memory={0x20027b40:callback,0x20027b44:argument,0xa0003018:ack}
    for _ in range(24):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('RTC ISR frame')
            saved=r['r15'];r['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('RTC ISR restore')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('RTC ISR ABI')
            return trace,r['r0']
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='br':nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('RTC ISR load operand')
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if a not in memory:raise ValueError('RTC ISR read address')
            r[reg]=memory[a];trace.append(('read',a,memory[a]))
        elif op=='jsr':
            if not callback or r[args]!=callback:raise ValueError('RTC callback target')
            trace.append(('call',r[args],r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xa5721368+i*0x113)&MASK
            r['r0']=result
        else:raise ValueError('Unhandled RTC ISR instruction '+op)
        pc=nxt
    raise ValueError('RTC ISR execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    attribution=analyze()
    candidate=build();build_getter();programs();out=ROOT/'build/gx8002-board'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfc0c','--stop-address=0xfc2c',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'rtc-isr-candidate.disassembly.txt').read_text());count=0
    for args in product((0,4,31,0x80000000,MASK),(0,0x10207000,0x10026000),
                        (0,0x20030000,MASK),(0,1,0x80000000,MASK),(0,1,MASK)):
        want=expected(*args)
        if execute(old,0xfc0c,*args)!=want or execute(new,ADDRESS,*args)!=want:raise ValueError('RTC ISR decoded mismatch')
        count+=1
    if not candidate['fits']:raise ValueError('RTC ISR exceeds slot')
    row={key:candidate[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfc0c,'bytes':32,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in
            ('verify_gx8002_rtc_isr.py','build_gx8002_rtc_isr_candidate.py','analyze_gx8002_rtc_primitives.py')}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(out/'rtc-isr-candidate.elf',output/'rtc-isr.elf')
    return {'functions':[row],'attribution':attribution,'candidate':candidate,'decoded_cases':count,'evidence_sha256':hashes,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Callback body modeled by return and caller clobbers; decoded call arguments/read order/ABI checked. No physical acknowledgement effect, concurrency or nested callback-stack proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-isr-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded RTC ISR cases:',report['decoded_cases'])
