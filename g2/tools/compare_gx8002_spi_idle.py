#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check busy-bit polling using decoded source and stock instructions."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_transport import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,values):
    r={};trace=[]
    for _ in range(300):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), 0x28\)',args)
            if not m or r[m[2]]+0x28!=0xa2000028:raise ValueError('unknown status read')
            if len(trace)>=len(values):return {'waiting':True,'reads':trace}
            value=values[len(trace)];trace.append(value);r[m[1]]=value
        elif op=='bnez':
            if r[p[0]]:next_pc=int(p[1],0)
        elif op=='rts':return {'waiting':False,'reads':trace,'result':r['r0']}
        else:raise ValueError('unexpected idle instruction')
        pc=next_pc
    raise ValueError('idle bound exceeded')


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'idle-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15660','--stop-address=0x15670',str(w)],text=True))
    new=decode((out/'transport-linked.disassembly.txt').read_text());cases=0
    for busy in (1,3,0xffffffff,0x80000001):
        for idle in (0,2,0xfffffffe,0x80000000):
            for count in (0,1,2,16):
                values=[busy]*count+[idle]
                expected={'waiting':False,'reads':values,'result':0}
                if execute(old,0x15660,values)!=expected or execute(new,0x1002364c,values)!=expected:raise ValueError('poll mismatch')
                cases+=1
        values=[busy]*16;expected={'waiting':True,'reads':values}
        if execute(old,0x15660,values)!=expected or execute(new,0x1002364c,values)!=expected:raise ValueError('wait mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Finite busy traces demonstrate continued polling, not physical liveness.', 'RX/TX helpers and full transport still need composed trace verification.']}
    (ROOT/'docs/research/gx8002-spi-idle-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
