#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded RTC tick register contracts, independent of physical timing."""
import hashlib,json,re,shutil,subprocess
from verify_gx8002_logging import check_paths
from analyze_gx8002_rtc_primitives import analyze
from build_gx8002_rtc_start_tick_candidate import ROOT,build as start
from build_gx8002_rtc_set_tick_candidate import build as set_tick
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,entry,value,operation):
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r['r0']=value;initial=r.copy();trace=[];pc=entry
    for _ in range(12):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('RTC memory operand')
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            if address!=(0xa000300c if operation=='start' else 0xa0003008):raise ValueError('RTC register address')
            if op=='ld.w':r[reg]=value;trace.append(('read',address,value))
            else:trace.append(('write',address,r[reg]))
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('RTC leaf ABI')
            return trace
        else:raise ValueError('Unhandled RTC instruction '+op)
        pc+=width
    raise ValueError('RTC execution bound')


def expected(value,operation):
    if operation=='start':return [('read',0xa000300c,value),('write',0xa000300c,value|4)]
    return [('write',0xa0003008,value)]


def verify():
    candidates={'start':start(),'set':set_tick()};build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-board'
    count=0
    values=[0,MASK,*range(256),*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for operation,offset,end,address,name in (('start',0xfc2c,0xfc3c,0x102066a0,'start'),('set',0xfc3c,0xfc48,0x102066b0,'set')):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={offset:#x}',f'--stop-address={end:#x}',str(out/'padmux-get-stock.elf')],text=True))
        new=decode((out/f'rtc-{name}-tick-candidate.disassembly.txt').read_text())
        for value in values:
            if execute(old,offset,value,operation)!=expected(value,operation) or execute(new,address,value,operation)!=expected(value,operation):raise ValueError('RTC decoded mismatch')
            count+=1
    return {'candidates':candidates,'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite register patterns and decoded leaf ABI; no physical RTC timing or concurrency proof. Admission export and evidence pinning pending.']}


def verify_one(operation,prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    if operation not in ('start','set'):raise ValueError('Unknown RTC operation')
    attribution=analyze();qualification=verify();candidate=qualification['candidates'][operation]
    if not candidate['fits']:raise ValueError('RTC tick exceeds slot')
    offset,size=(0xfc2c,16) if operation=='start' else (0xfc3c,12)
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':offset,'bytes':size,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=['verify_gx8002_rtc_ticks.py','analyze_gx8002_rtc_primitives.py',
           'build_gx8002_rtc_start_tick_candidate.py','build_gx8002_rtc_set_tick_candidate.py',
           'verify_gx8002_rtc_'+operation+'_tick.py']
    hashes={n:hashlib.sha256((ROOT/'tools'/n).read_bytes()).hexdigest() for n in names}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/f'build/gx8002-board/rtc-{operation}-tick-candidate.elf',output/f'rtc-{operation}-tick.elf')
    return {'functions':[row],'qualification':qualification,'attribution':attribution,
            'evidence_sha256':hashes,'source_admitted':True,'hardware_qualified':False,
            'limits':['Decoded finite register patterns and leaf ABI, authenticated SDK attribution. No physical RTC timing or concurrent access proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-ticks-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded RTC cases:',report['decoded_cases'])
