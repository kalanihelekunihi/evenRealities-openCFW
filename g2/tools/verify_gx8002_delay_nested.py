# SPDX-License-Identifier: MIT
"""Decoded millisecond wrapper and delay polling with source counter conversion."""
import json,subprocess
from verify_gx8002_delay import verify as boundaries,expected
from execute_gx8002_delay import execute
from verify_gx8002_clock_time_us_candidate import execute as convert
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def wrapper(code,entry,msec):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=msec,r14=0x20070000);initial=r.copy();pc=entry;call=None
    for _ in range(12):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));assert call is not None;return call
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=r[p[1]]<<int(p[2],0)
        elif op=='mult':r[p[0]]=(r[p[0]]*r[p[1]])&0xffffffff
        elif op=='bsr':
            assert int(args,0)+(0x1000dfec if entry<0x100000 else 0)==0x10025944;assert call is None;call=r['r0']
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Wrapper bound')

def verify():
    evidence=boundaries();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17958','--stop-address=0x179b0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-board/delay-candidate.disassembly.txt').read_text())
    p=ROOT/'build/gx8002-board/clock-time-us-candidate.elf';elf=Elf32(p.read_bytes(),'timer');report=json.loads((ROOT/'docs/research/gx8002-clock-time-us-source-verification.json').read_text());row=report['functions'][0];sec=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(sec))==row['compiled_sha256'];timer=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    def runner(ticks):return convert(timer,ticks&0xffffffff,ticks>>32)
    cases=0
    for msec in (0,1,2,4294967,4294968,0x7fffffff,0xffffffff):
        usec=(msec*1000)&0xffffffff;assert wrapper(old,0x179a0,msec)==wrapper(new,0x1002598c,msec)==usec
        for start in (0,1023,0xffffffff,(1<<64)//1000-1,(1<<64)-2):
            for delta in (0,1,1024,2048,(usec+2)*1024):
                ticks=[start,(start+delta)&((1<<64)-1)];times=[((x*1000)&((1<<64)-1))//1024 for x in ticks]
                assert execute(old,0x17958,usec,ticks,runner)==execute(new,0x10025944,usec,ticks,runner)==expected(usec,times),(msec,start,delta);cases+=1
    return {'boundaries':evidence,'cases':cases,'timer_elf_sha256':sha(p.read_bytes()),'source_admitted':False,'limits':['Decoded millisecond wrapper ABI/argument checks composed with delay execution and decoded timer using marshalled raw counter words. Backoff instruction counts checked; physical cycle/clock timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-delay-nested.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
