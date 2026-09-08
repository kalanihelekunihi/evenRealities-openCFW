#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded device-configuration comparison with byte-producing transport."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_device_candidate import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,status,seed):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();saved=None;byte=None;trace=[];low=r['r14']
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('unexpected frame')
            saved=r['r15'];r['r14']-=4
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','andi','ori','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op=='subi' else a&b if op=='andi' else a|b)&0xffffffff
        elif op in ('ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \(r14, 0x3\)',args)
            if not m or r['r14']!=initial['r14']-8:raise ValueError('unexpected byte address')
            if op=='ld.b':
                if byte is None:raise ValueError('uninitialized status byte')
                r[m[1]]=byte
            else:byte=r[m[1]]&255
        elif op=='bnez':
            if r[p[0]]!=0:following=int(p[1],0)
        elif op=='bsr':
            target=int(args,0)+delta
            if target in (0x10023684,0x100236dc):
                command=0x15 if target==0x10023684 else 0x11
                if (r['r0'],r['r1'],r['r2'])!=(command,r['r14']+3,1):raise ValueError('transport argument mismatch')
                if target==0x10023684:byte=status;trace.append(['read',command,1,status])
                else:
                    if byte is None:raise ValueError('uninitialized write')
                    trace.append(['write',command,1,byte])
            elif target in (0x1002375c,0x1002374c):trace.append(['call',target])
            else:raise ValueError('unknown device call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xdeadbeef^i)&0xffffffff
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
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'device-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x16300','--stop-address=0x16344',str(wrapper)],text=True))
    new=decode((out/'device.disassembly.txt').read_text());cases=0
    for status in range(256):
        trace=[['read',21,1,status]]
        if not status&16:trace += [['call',0x1002375c],['call',0x1002374c],['write',17,1,status|16],['call',0x1002375c]]
        expected={'result':0,'trace':trace,'frame_bytes':8}
        for seed in (0,0xffffffff,0x55555555,0xaaaaaaaa):
            if execute(old,0x16300,0x1000dfec,status,seed)!=expected or execute(new,0x100242ec,0,status,seed)!=expected:raise ValueError('device trace mismatch')
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Source-qualified read transport initializes one byte on completion; polling has no timeout.','Transport/control calls are modeled with ABI clobbers; hardware effects are not qualified.']}
    (ROOT/'docs/research/gx8002-flash-device-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
