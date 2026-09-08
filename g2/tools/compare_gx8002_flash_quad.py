#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded device-configuration comparison with byte-producing transport."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_quad import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,status,seed,first=0,paired=False):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();saved=None;byte={};trace=[];low=r['r14']
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('unexpected frame')
            saved=r['r15'];r['r14']-=4
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','andi','ori','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op=='subi' else a&b if op=='andi' else a|b)&0xffffffff
        elif op in ('ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \(r14, (0x[0-9a-f]+)\)',args)
            if not m or r['r14']!=initial['r14']-8:raise ValueError('unexpected byte address')
            offset=int(m[2],0)
            if not 0<=offset<4:raise ValueError('byte outside frame')
            if op=='ld.b':
                if offset not in byte:raise ValueError('uninitialized status byte')
                r[m[1]]=byte[offset]
            else:byte[offset]=r[m[1]]&255
        elif op=='bnez':
            if r[p[0]]!=0:following=int(p[1],0)
        elif op=='bsr':
            target=int(args,0)+delta
            result=0
            if target in (0x10023734,0x10023770):
                result=first if target==0x10023734 else status
                trace.append(['status',target,result])
            elif target==0x100236dc:
                command,count,offset=(1,2,0) if paired else (49,1,3)
                if (r['r0'],r['r1'],r['r2'])!=(command,r['r14']+offset,count):raise ValueError('transport argument mismatch')
                if any(i not in byte for i in range(offset,offset+count)):raise ValueError('uninitialized write')
                trace.append(['write',command,[byte[i] for i in range(offset,offset+count)]])
            elif target in (0x1002375c,0x1002374c):trace.append(['call',target])
            else:raise ValueError('unknown quad call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xdeadbeef^i)&0xffffffff
            r['r0']=result
        elif op=='pop':
            if args!='r15' or saved is None or r['r14']!=initial['r14']-4:raise ValueError('unbalanced frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI mismatch')
            return {'result':r['r0'],'trace':trace,'frame_bytes':initial['r14']-low}
        else:raise ValueError('unsupported device instruction '+op)
        low=min(low,r['r14']);pc=following
    raise ValueError('device execution bound exceeded')


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'quad-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x162c8','--stop-address=0x16380',str(wrapper)],text=True))
    new=decode((out/'quad-linked.disassembly.txt').read_text());cases=0
    for paired in (False,True):
        for first in (range(256) if paired else [0]):
            for status in range(256):
                trace=([['status',0x10023734,first]] if paired else [])+[['status',0x10023770,status]]
                if not status&2:trace += [['call',0x1002375c],['call',0x1002374c],['write',1 if paired else 49,[first,status|2] if paired else [status|2]],['call',0x1002375c]]
                expected={'result':0,'trace':trace,'frame_bytes':8}
                for seed in (0,0xffffffff):
                    entry=0x16344 if paired else 0x162c8
                    if execute(old,entry,0x1000dfec,status,seed,first,paired)!=expected or execute(new,entry+0x1000dfec,0,status,seed,first,paired)!=expected:raise ValueError('quad trace mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Source-qualified status and transport contracts; control calls modeled with ABI clobbers.', 'No physical hardware qualification; polling has no timeout.']}
    (ROOT/'docs/research/gx8002-flash-quad-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
