#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute FIFO-empty waits and their nested idle helper continuously."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_transport import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,values,idle_entry):
    r={f'r{i}':0x12340000+i for i in range(32)};initial=r.copy();trace=[];saved=None;return_pc=None
    for _ in range(300):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('unexpected save')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown status read')
            address=r[m[2]]+int(m[3],0)
            if address not in (0xa2000020,0xa2000024,0xa2000028):raise ValueError('unknown status read')
            if len(trace)>=len(values):return {'waiting':True,'reads':trace}
            expected_address,value=values[len(trace)]
            if address!=expected_address:raise ValueError('read order mismatch')
            trace.append([address,value]);r[m[1]]=value
        elif op=='bnez':
            if r[p[0]]:next_pc=int(p[1],0)
        elif op=='bsr':
            if int(args,0)!=idle_entry or return_pc is not None:raise ValueError('unexpected nested call')
            return_pc=next_pc;r['r15']=next_pc;next_pc=idle_entry
        elif op=='rts':
            if return_pc is None:raise ValueError('unexpected idle return')
            next_pc=return_pc;return_pc=None
        elif op=='pop':
            if args!='r4, r15' or saved is None or return_pc is not None:raise ValueError('unbalanced return')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('ABI mismatch')
            return {'waiting':False,'reads':trace,'result':r['r0']}
        else:raise ValueError('unexpected idle instruction')
        pc=next_pc
    raise ValueError('idle bound exceeded')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'empty-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15660','--stop-address=0x15698',str(w)],text=True))
    new=decode((out/'transport-linked.disassembly.txt').read_text());cases=0
    for entry,address in ((0x15670,0xa2000024),(0x15684,0xa2000020)):
        for fifo in (1,7,0xffffffff):
            for count in (0,1,8):
                for busy_count in (0,1,8):
                    values=[[address,fifo]]*count+[[address,0]]+[[0xa2000028,0xffffffff]]*busy_count+[[0xa2000028,0xfffffffe]]
                    expected={'waiting':False,'reads':values,'result':0}
                    if execute(old,entry,values,0x15660)!=expected or execute(new,entry+0x1000dfec,values,0x1002364c)!=expected:raise ValueError('empty wait mismatch')
                    cases+=1
        for values in ([[address,7]]*16,[[address,0]]+[[0xa2000028,1]]*16):
            expected={'waiting':True,'reads':values}
            if execute(old,entry,values,0x15660)!=expected or execute(new,entry+0x1000dfec,values,0x1002364c)!=expected:raise ValueError('continued wait mismatch')
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Finite status schedules model hardware reads; no hardware liveness proof.','Full command transport/buffer behavior remains unqualified.']}
    (ROOT/'docs/research/gx8002-spi-empty-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
