#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute both query bodies, including their actual nested call and MMIO reads."""
import contextlib
import io
import itertools
import json
import re
import struct
import subprocess
from build_gx8002_start_mode_candidate import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code, pc, memory, reason_entry):
    regs={f'r{i}':0x12340000+i for i in range(32)}
    initial=regs.copy();stack=[];trace=[];returns=[];carry=None
    for _ in range(100):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];following=pc+width
        if op in ('movi','movih'):
            regs[p[0]]=int(p[1],0) << (16 if op=='movih' else 0)
        elif op in ('lsli','andi','subi'):
            a=regs[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            regs[p[0]]=(a<<b if op=='lsli' else a&b if op=='andi' else a-b)&0xffffffff
        elif op=='ld.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('unsupported MMIO load')
            dest,base,offset=match.groups();address=regs[base]+int(offset,0)
            if address not in memory:raise ValueError('unknown MMIO read')
            regs[dest]=memory[address];trace.append([address,memory[address]])
        elif op=='cmphsi':carry=regs[p[0]]>=int(p[1],0)
        elif op in ('br','bt','bnez'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or op=='bt' and carry or op=='bnez' and regs[p[0]]!=0:following=int(p[-1],0)
        elif op=='push':
            if args!='r15' or stack:raise ValueError('unexpected save')
            stack.append(regs['r15']);regs['r14']-=4
        elif op=='bsr':
            if int(p[0],0)!=reason_entry or returns:raise ValueError('unknown nested call')
            returns.append(following);regs['r15']=following;following=reason_entry
        elif op in ('rts','pop'):
            if op=='pop':
                if args!='r15' or not stack or returns:raise ValueError('unexpected return')
                regs['r15']=stack.pop();regs['r14']+=4
            if returns:following=returns.pop()
            else:
                if stack or any(regs[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('ABI mismatch')
                return regs['r0'],trace
        else:raise ValueError('unsupported query instruction '+op)
        pc=following
    raise ValueError('query instruction bound exceeded')


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-start-mode';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x16954','--stop-address=0x169b8',str(wrapper)],text=True))
    new=decode((out/'mode.disassembly.txt').read_text());cases=0
    for bits,upper,fallback,mode,discard in itertools.product(range(16),(0,0xfffffff0,0x80000000),(0,1,0xfffffffe,0xffffffff),(0,1,0xfffffffe,0xffffffff),(0,0xffffffff)):
        status=bits|upper;mem={0xa0000034:status,0xa001002c:fallback,0xa0010058:mode,0xa001005c:discard}
        # Fixed table is independent of the emitted priority branches.
        reason=(fallback&1,2,4,2,3,2,3,2,5,2,5,2,3,2,3,2)[bits]
        reads=[[0xa0000034,status]]
        if bits==0:reads += [[0xa001002c,fallback]]
        expected_mode=(mode&1) if bits else 0
        mode_reads=reads+([[0xa0010058,mode],[0xa001005c,discard]] if bits else [])
        for code,re,mo in ((old,0x16954,0x16998),(new,0x10024940,0x10024984)):
            if execute(code,re,mem,re)!=(reason,reads) or execute(code,mo,mem,re)!=(expected_mode,mode_reads):raise ValueError('query trace mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,
            'limits':['Models reads as supplied values; no hardware side-effect or timing qualification.',
                      'All low status-bit combinations covered; upper bits and register data use representative patterns.']}
    (ROOT/'docs/research/gx8002-start-mode-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report


if __name__=='__main__':verify()
