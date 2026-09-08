#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the decoded MPU prefix against stock and an independent mask oracle."""
import itertools
import json
import re
import struct
import subprocess
from build_gx8002_system_candidate import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code, pc, controls, full=False, mode=0, delta=0, seed=0):
    regs={f'r{i}':0x12340000+i for i in range(32)}
    trace=[];initial=regs.copy();saved=None
    for _ in range(100):
        op,args,width=code[pc]
        if op=='bsr' and not full:return trace
        following=pc+width
        p=[s.strip() for s in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('unexpected frame')
            saved=regs['r15'];regs['r14']-=4
        elif op in ('mfcr','mtcr'):
            match=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args)
            if not match:raise ValueError('unknown control register syntax')
            reg,idx=match.groups();idx=int(idx)
            if idx not in ((1,18,19,20,21) if full else (18,19,20,21)):raise ValueError('unexpected control register')
            if op=='mfcr':regs[reg]=controls[idx];trace.append(['read',idx,controls[idx]])
            else:trace.append(['write',idx,regs[reg]])
        elif op in ('movi','lrw','movih'):
            regs[p[0]]=int(p[1],0) << (16 if op=='movih' else 0)
        elif op=='mov':regs[p[0]]=regs[p[1]]
        elif op=='ins':
            high,low=int(p[2]),int(p[3]);mask=((1<<(high-low+1))-1)<<low
            regs[p[0]]=(regs[p[0]]&~mask)|((regs[p[1]]<<low)&mask)
        elif op in ('addi','subi','andi','ori','and','andn'):
            a=regs[p[0] if len(p)==2 else p[1]]
            b=regs[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            regs[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&b if op in ('andi','and') else a|b if op=='ori' else a&~b)&0xffffffff
        elif full and op=='bsr':
            target=int(p[0],0)+delta
            if target not in (0x10025a88,0x10024984,0x10023528,0x10025cbc):raise ValueError('unexpected service call')
            trace.append(['call',target])
            for i in (0,1,2,3,12,13,15):regs[f'r{i}']=(seed^0xdeadbeef^(i*0x1020304))&0xffffffff
            if target==0x10024984:regs['r0']=mode&0xffffffff
        elif full and op in ('br','bez','bnez'):
            if op=='br' or (regs[p[0]]==0)==(op=='bez'):following=int(p[-1],0)
        elif full and op=='st.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('unexpected MMIO syntax')
            value,base,offset=match.groups();address=regs[base]+int(offset,0)
            if address not in (0xe000ec10,*(0xe000e300+i*4 for i in range(4)),*(0xe000e280+i*4 for i in range(4))):raise ValueError('unexpected MMIO address')
            trace.append(['mmio',address,regs[value]])
        elif full and op=='psrset':
            if args!='ee, ie':raise ValueError('unexpected PSR enable')
            trace.append(['enable','ee','ie'])
        elif full and op=='pop':
            if args!='r15' or saved is None:raise ValueError('unexpected return frame')
            regs['r15']=saved;regs['r14']+=4
            if any(regs[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI mismatch')
            return trace
        else:raise ValueError('unsupported MPU instruction '+op)
        pc=following
    raise ValueError('MPU prefix bound exceeded')


def verify():
    evidence=build();out=ROOT/'build/gx8002-system';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=out/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x15560','--stop-address=0x155ac',str(wrapper)],text=True))
    new=decode((out/'system.disassembly.txt').read_text());cases=0
    patterns=(0,0xffffffff,0x55555555,0xaaaaaaaa,0x01000301,0xfffff0c0)
    for values in itertools.product(patterns,repeat=4):
        c=dict(zip((18,19,20,21),values))
        expected=[['read',19,c[19]],['read',20,c[20]],['read',21,c[21]],
                  ['write',21,c[21]&0xfffffff8],['write',19,(c[19]&0xfefffcfe)|0x300],
                  ['write',20,(c[20]&0xfff)|0x3f],['read',18,c[18]],['write',18,c[18]|3]]
        if execute(old,0x15560,c)!=expected or execute(new,0x1002354c,c)!=expected:raise ValueError('MPU trace mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,
            'limits':['Only the MPU prefix is compared; later calls and VIC writes remain unqualified.',
                      'Register reads modeled as supplied values; hardware timing and access faults excluded.']}
    (ROOT/'docs/research/gx8002-system-mpu-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases)
    return report


if __name__=='__main__':verify()
