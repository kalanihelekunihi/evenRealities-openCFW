#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded OTP descriptor accessors; no physical OTP writes are performed."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_backup_otp_region import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,argument,events):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r0']=argument;initial=r.copy();index=0;carry=None
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('subi','andi','andni','and','or'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a&~b if op=='andni' else a|b if op=='or' else a&b)&0xffffffff
        elif op=='cmphs':carry=r[p[0]]>=r[p[1]]
        elif op in ('bt','br'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or carry:n=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown address')
            reg,base,offset=m.groups();address=r[base]+int(offset,0)
            if index>=len(events):raise ValueError('extra access')
            e=events[index];index+=1
            if e[:2]!=['read' if op=='ld.w' else 'write',address] or op=='st.w' and e[2]!=r[reg]:raise ValueError('access mismatch')
            if op=='ld.w':r[reg]=e[2]
        elif op=='rts':
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('return state mismatch')
            return r['r0']
        else:raise ValueError('unknown OTP instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')


def oracle(kind,argument,count,flags,size,device=0x20029000,descriptor=0x20029100):
    events=[['read',0x20016d6c,device],['read',device+20,descriptor]]
    if kind=='set':
        events.append(['read',descriptor+12,count])
        if argument>=count:return 0xffffffff,events
        events.extend([['read',descriptor+16,flags],['write',descriptor+16,(flags&0xfffffff8)|argument]])
    else:
        offset,value={'count':(12,count),'current':(16,flags),'size':(8,size)}[kind]
        events.extend([['read',descriptor+offset,value],['write',argument,value&7 if kind=='current' else value]])
    return 0,events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-backup-otp-region';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'otp-region-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x3fc28','--stop-address=0x3fc90',str(wrapper)],text=True));new=decode((out/'otp-region-linked.disassembly.txt').read_text());cases=0
    flags_set=[*range(256),*[1<<i for i in range(8,32)],0x7fffffff,0x80000000,0xffffffff]
    for count in (0,1,3,7,8,9,0x7fffffff,0x80000000,0xffffffff):
        for flags in flags_set:
            for argument in (0,1,2,3,7,8,9,(count-1)&0xffffffff,count,0xffffffff):
                expected,events=oracle('set',argument,count,flags,512)
                if execute(old,0x3fc3c,argument,events)!=expected or execute(new,0x100072fc,argument,events)!=expected:raise ValueError('selection mismatch')
                cases+=1
            for kind,entry in (('count',0x3fc28),('current',0x3fc64),('size',0x3fc7c)):
                for output in (0x20028000,0x20029110):
                    expected,events=oracle(kind,output,count,flags,flags)
                    if execute(old,entry,output,events)!=expected or execute(new,entry-0x38940+0x10000000,output,events)!=expected:raise ValueError('getter mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Valid aligned selected-device, descriptor and output pointers; output alias with descriptor flags included.', 'Source descriptor layout is checked by the builder; device-record ownership and physical OTP operations remain unqualified.'], 'coverage':['Unsigned region/count boundaries including counts above eight; all low-byte flags and every high bit.', 'All pointer-chain reads, descriptor mutations, output stores and preserved registers.']}
    (ROOT/'docs/research/gx8002-backup-otp-region-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
