# SPDX-License-Identifier: MIT
"""Decoded millisecond wrapper call/ABI boundaries."""
import json,random,subprocess
from build_gx8002_clock_time_ms_candidate import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,value,divider=None):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=entry;saved=None;calls=[]
    for _ in range(20):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0']|(r['r1']<<32),calls
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=r[p[1]]<<int(p[2],0)
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0)
            if target==0x1002585c:result=value;calls.append(('time',value))
            else:
                assert target==0x10209aa4;left=r['r0']|(r['r1']<<32);right=r['r2']|(r['r3']<<32);assert (left,right)==(value,1000);result=divider(left,right) if divider else left//right;calls.append(('divide',left,right))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff;r['r1']=result>>32
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Execution bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17944','--stop-address=0x17958',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-time-ms-candidate.disassembly.txt').read_text());rng=random.Random(1000);values=[0,1,999,1000,1001,0xffffffff,1<<32,(1<<64)-1]+[rng.getrandbits(64) for _ in range(1024)]
    for value in values:assert execute(old,0x17944,value)==execute(new,0x10025930,value)==(value//1000,[('time',value),('divide',value,1000)])
    from execute_gx8002_udivdi3 import execute as divide
    from verify_gx8002_clock_time_us_candidate import execute as timer
    codes={};hashes={}
    for name,path,report_name in (('timer',ROOT/'build/gx8002-board/clock-time-us-candidate.elf','gx8002-clock-time-us-source-verification.json'),('division',ROOT/'build/gx8002-udivdi3/candidate.elf','gx8002-udivdi3-source-verification.json')):
        elf=Elf32(path.read_bytes(),name);reviewed=json.loads((ROOT/'docs/research'/report_name).read_text())
        for row in reviewed['functions']:
            sec=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(sec))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));hashes[name]=sha(path.read_bytes())
    def divider(a,b):return divide(codes['division'],0x10209aa4,a,b,raw=True)
    for ticks in values:
        value=timer(codes['timer'],ticks&0xffffffff,ticks>>32)
        assert value==((ticks*1000)&((1<<64)-1))//1024
        assert execute(old,0x17944,value,divider)==execute(new,0x10025930,value,divider)==(value//1000,[('time',value),('divide',value,1000)])
    return {'candidate':candidate,'cases':len(values),'nested_cases':len(values),'dependency_elf_sha256':hashes,'source_admitted':False,'limits':['Decoded stock/source wrapper call arguments, quotient and ABI checked. Additional decoded source timer/division integration checked with marshalled raw counter/result frames. Physical counter timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-time-ms.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
