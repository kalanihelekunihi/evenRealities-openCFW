# SPDX-License-Identifier: MIT
"""Decode primary NOR loader call arguments; do not assume physical RAM alias."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-D','--start-address=0xa02a','--stop-address=0xa04c',str(path)],text=True))
    r={'r5':0x3000,'r6':0x10023400,'r14':0x20010000};calls=[];pc=0xa02a
    while pc<=0xa044:
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='mov':r[p[0]]=r[p[1]]
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='ld.w':assert args=='r0, (r14, 0x0)';r['r0']=0x8e84
        elif op in ('addu','subu','addi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=(a-b if op=='subu' else a+b)&0xffffffff
        elif op=='bsr':assert int(args,0)==0xa1e4;calls.append([r['r0'],r.get('r1',r['r14']),r.get('r2',4)])
        else:raise ValueError((op,args))
        pc+=width
    assert calls==[[0x3000,0x20010000,4],[0xbe88,0x10023400,0x397c]]
    assert int.from_bytes(stock[0xc58c:0xc590],'little')==0x8e84
    offset=0x18aa8-(0x958c+calls[1][0]);assert offset==0x3694 and offset+256<=calls[1][2]
    return {'stock_sha256':IMAGE_SHA,'routine_package_offset':0x9fd0,'primary_path_sha256':sha(stock[0xa02a:0xa04c]),'flash_calls':calls,'uart_destination_iram':calls[1][1]+offset,'uart_expected_dram':0x20026a94,'source_admitted':False,'limits':['Decoded primary call arguments under boot_addr0 and authenticated XIP length. Actual flash reader, preceding branch/setup, and physical IRAM/DRAM alias not executed here. UART bytes lie within requested copy; not proof of completed hardware transfer.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-descriptor-loader.json').write_text(json.dumps(r,indent=2)+'\n');print(r['flash_calls'])
