#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate reboot writes and terminal wait without resetting hardware."""
import json
import re
import struct
import subprocess
from link_gx8002_reboot import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,start,delta):
    r={f'r{i}':0x98760000+i for i in range(32)};trace=[];pc=start
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15':raise ValueError('unexpected save')
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bsr':
            target=(int(p[0],0)+delta)&0xffffffff
            if target==0x102067b8:
                trace.append(('reboot',));following=int(p[0],0)
            elif target==0x10025080:
                trace.append(('gate',r['r0'],r['r1']))
                for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            else:raise ValueError('unexpected call')
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported write operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a not in (0xa001002c,0xa0700000,0xa0700004,0xa070000c):raise ValueError('unexpected write')
            trace.append(('write',a,r[reg]))
        elif op=='br':
            if int(p[0],0)!=pc:raise ValueError('unexpected branch')
            return trace+[('reset_wait',)]
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=link();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=output/'reboot-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old={}
    for low,high in ((0xfd44,0xfd68),(0x12224,0x1222c)):
        old.update(decode(subprocess.check_output([str(prefix)+'objdump','-D',f'--start-address={low}',f'--stop-address={high}',str(wrapper)],text=True)))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(output/'reboot.elf')],text=True))
    expected=[('gate',24,1),('write',0xa001002c,1),('write',0xa0700000,0),('write',0xa0700004,0),('write',0xa070000c,118),('write',0xa0700000,1),('reset_wait',)]
    for callback in (False,True):
        offset=0x12224 if callback else 0xfd44;oracle=([('reboot',)] if callback else [])+expected
        if execute(old,offset,0x101f6a74)!=oracle or execute(new,offset+0x101f6a74,0)!=oracle:raise ValueError('reboot trace mismatch')
    report={'placement':evidence,'entry_paths':2,'trace':[list(item) for item in expected],'source_admitted':False,
            'limits':['Gate call modeled; decoded execution stops at the verified self-loop.', 'No physical reset or hardware watchdog timing qualification.']}
    (ROOT/'docs/research/gx8002-reboot-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('two reboot paths verified');return report

if __name__=='__main__':verify()
