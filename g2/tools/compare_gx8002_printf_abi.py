#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify printf register/stack argument forwarding in decoded target code."""
import json
import random
import re
import struct
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_memcpy_source import decode
from link_gx8002_uart_console import ROOT


def execute(code,start,target,values,result):
    r={f'r{i}':0x98760000+i for i in range(32)}
    r.update(r0=0x1000,r14=0x9000,r15=0x12345678)
    for i in range(3):r[f'r{i+1}']=values[i] if i<len(values) else 0xabcdef00+i
    initial=r.copy();memory={a:0xa5 for a in range(0x8f00,0x9100)}
    def write(a,v):
        if any(a+i not in memory for i in range(4)):raise ValueError('outside stack')
        for i in range(4):memory[a+i]=(v>>(8*i))&255
    def read(a):
        if any(a+i not in memory for i in range(4)):raise ValueError('outside stack')
        return sum(memory[a+i]<<(8*i) for i in range(4))
    for i,v in enumerate(values[3:]):write(0x9000+4*i,v)
    before=memory.copy();pc=start;calls=[]
    for _ in range(100):
        op,args,size=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported operand')
            reg,ptr,off=m.groups();a=r[ptr]+int(off,0)
            if op=='ld.w':r[reg]=read(a)
            else:write(a,r[reg])
        elif op=='push':
            if args!='r15':raise ValueError('unsupported push')
            r['r14']-=4;write(r['r14'],r['r15'])
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if int(p[0],0)!=target:raise ValueError('wrong formatter call')
            calls.append((r['r0'],r['r1'],[read(r['r2']+4*i) for i in range(len(values))]))
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI restore mismatch')
            if any(memory[a]!=before[a] for a in range(0x9000,0x9100)):raise ValueError('caller stack changed')
            return r['r0'],calls
        else:raise ValueError('unsupported instruction '+op)
        pc+=size
    raise ValueError('execution bound exceeded')


def verify():
    output=ROOT/'build/gx8002-printf';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_printf.c'
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    script=output/'printf.ld'
    script.write_text('SECTIONS { .text.open_cfw_gx8002_printf 0x10206c24 : { *(.text.open_cfw_gx8002_printf) } open_cfw_gx8002_tfp_format = 0x10206a84; /DISCARD/ : { *(.comment) *(.note*) } }\n')
    subprocess.run([str(prefix)+'gcc',*FLAGS,'-c',str(source),'-o',str(output/'printf.o')],check=True)
    subprocess.run([str(prefix)+'ld','-T',str(script),str(output/'printf.o'),'-o',str(output/'printf.elf')],check=True)
    wrapper=output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x101b0','--stop-address=0x101ce',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(output/'printf.elf')],text=True))
    rng=random.Random(804);cases=0
    for count in range(17):
      for _ in range(16):
        values=[rng.randrange(2**32) for i in range(count)]
        for result in (0,1,0x7fffffff,0xffffffff):
            expected=(result,[(0,0x1000,values)])
            if execute(old,0x101b0,0x10010,values,result)!=expected or execute(new,0x10206c24,0x10206a84,values,result)!=expected:raise ValueError('printf forwarding mismatch')
            cases+=1
    elf=Elf32((output/'printf.elf').read_bytes(),'printf');section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_printf')
    if section['size']>30 or elf.relocations(section['index']):raise ValueError('wrapper placement failure')
    report={'source_sha256':sha(source.read_bytes()),'flags':FLAGS,'compiled_bytes':section['size'],
            'compiled_sha256':sha(elf.contents(section)),'cases':cases,'source_admitted':False,
            'limits':['Modeled formatter call and 32-bit argument slots only; no hardware timing claim.',
                      'Firmware integration remains pending.']}
    (ROOT/'docs/research/gx8002-printf-abi-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
