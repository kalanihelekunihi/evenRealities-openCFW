#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded clock divider load sequence and leaf ABI."""
import hashlib,json,re,shutil,subprocess
from verify_gx8002_logging import check_paths
from itertools import product
from build_gx8002_clock_divider_candidate import ROOT,build
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
PARAM=0x20031000
DIV=0x20031100
ADDRESS=0x10024ae8


def expected(present,base,offset,shift,mask,word):
    trace=[('read',PARAM+8,4,DIV if present else 0)]
    if not present:return trace,0
    trace.extend([('read',DIV,1,offset),('read',DIV+1,1,shift),('read',(base+offset)&MASK,4,word),('read',DIV+2,2,mask)])
    value=(word>>shift)&mask
    return trace,value+1 if value else 0


def execute(code,entry,present,base,offset,shift,mask,word):
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=PARAM,r1=base);initial=r.copy();pc=entry;trace=[];condition=False
    memory={(PARAM+8,4):DIV if present else 0,(DIV,1):offset,(DIV+1,1):shift,(DIV+2,2):mask,((base+offset)&MASK,4):word}
    for _ in range(24):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.b','ld.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Divider memory operand')
            reg,base_reg,imm=m.groups();a=(r[base_reg]+int(imm,0))&MASK;n={'ld.w':4,'ld.b':1,'ld.h':2}[op]
            if (a,n) not in memory:raise ValueError('Divider read address/width')
            r[reg]=memory[a,n];trace.append(('read',a,n,r[reg]))
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='lsr':
            if r[p[1]]>=32:raise ValueError('Unqualified divider shift')
            r[p[0]]>>=r[p[1]]
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Divider ABI')
            return trace,r['r0']
        else:raise ValueError('Unhandled divider instruction '+op)
        pc=nxt
    raise ValueError('Divider execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build();build_getter();programs();out=ROOT/'build/gx8002-board'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16afc','--stop-address=0x16b18',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'clock-divider-candidate.disassembly.txt').read_text());count=0
    for args in product((False,True),(0xa0010000,0xa0300000),(0,0x80,0x84,0x88,252),range(32),(0,1,0x3f,0x3ff,0xffff),(0,1,MASK,0x12345678)):
        want=expected(*args)
        if execute(old,0x16afc,*args)!=want or execute(new,ADDRESS,*args)!=want:raise ValueError('Divider decoded mismatch')
        count+=1
    if not candidate['fits']:raise ValueError('Divider exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0x16afc,'bytes':28,
                              'sha256':candidate['stock_sha256'],'region':'image_a_sram_text'}]
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in
            ('verify_gx8002_clock_divider.py','build_gx8002_clock_divider_candidate.py')}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(out/'clock-divider-candidate.elf',output/'clock-divider.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'evidence_sha256':hashes,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Valid distinct parameter/descriptor memory, aligned register addresses, shifts0..31. Exact read sequence and leaf ABI. No concurrent mutation or hardware effects proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-divider-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded divider cases:',report['decoded_cases'])
