#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted stock/source CRC instruction comparison, not a CPU emulator."""
import json
import random
import re
import struct
import subprocess
import zlib
from link_gx8002_crc_candidate import main as link_candidate, ROOT
from verify_gx8002_memcpy_source import decode
from generate_gx8002_crc_table import table_values
from analyze_gx8002_upstream_objects import IMAGE
TABLE=0x1020b908


def execute(code, start, seed, address, data):
    r={f'r{i}':0x98760000+i for i in range(32)}
    r.update(r0=seed,r1=address,r2=len(data))
    memory={address+i:b for i,b in enumerate(data)}
    memory.update({TABLE+i:b for i,b in enumerate(struct.pack('<256I',*table_values()))})
    pc=start;condition=False;trace=[]
    for _ in range(len(data)*30+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('andi','xor','addu','subi','addi','lsri','lsli'):
            a=r[p[0] if len(p)==2 else p[1]]
            b=r[p[-1]] if op in ('xor','addu') else int(p[-1],0)
            if op=='andi':value=a&b
            elif op=='xor':value=a^b
            elif op in ('addi','addu'):value=a+b
            elif op=='subi':value=a-b
            elif op=='lsri':value=a>>b
            else:value=a<<b
            r[p[0]]=value&0xffffffff
        elif op in ('cmpne','cmphsi'):
            condition=r[p[0]]!=r[p[1]] if op=='cmpne' else r[p[0]]>=int(p[1],0)
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            if (r[p[0]]==0 if op=='bez' else r[p[0]]!=0):following=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):following=int(p[0],0)
        elif op in ('ld.b','ldr.w','ldbi.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+)|, (r\d+) << ([02]))?\)',args)
            if not m:raise ValueError('unsupported memory operand: '+args)
            dest,base,imm,index,shift=m.groups()
            location=(r[base]+(r[index]<<int(shift) if index else int(imm or '0',0)))&0xffffffff
            size=1 if op=='ld.b' else 4
            if size==4 and location%4:raise ValueError('unaligned word read')
            if any(location+i not in memory for i in range(size)):raise ValueError('out-of-bounds read')
            trace.append((location,size));r[dest]=sum(memory[location+i]<<(i*8) for i in range(size))
            if op=='ldbi.w':r[base]=(r[base]+4)&0xffffffff
        elif op=='rts':return r['r0'],trace
        else:raise ValueError('unsupported instruction: '+op)
        pc=following
    raise ValueError('instruction bound exceeded')


def verify(prefix=None, sdk=None, output=None):
    out=output or ROOT/'build/gx8002-crc-linked'
    prefix=prefix or ROOT/'build/csky-macos/install/bin'
    placement=link_candidate(prefix, out)
    source=decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'),'-d',
                  '--section=.text.open_cfw_gx8002_crc32_no_comp',str(out/'crc.elf')],text=True))
    wrapper=out/'stock.elf'
    subprocess.run([str(prefix/'csky-unknown-elf-objcopy'),'-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    stock=decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'),'-D','--start-address=0x12d80','--stop-address=0x12e2e',str(wrapper)],text=True))
    rng=random.Random(0x12d80);cases=0
    for alignment in range(4):
        for size in range(257):
            data=bytes(rng.randrange(256) for _ in range(size));seed=rng.getrandbits(32)
            original,old_trace=execute(stock,0x12d80,seed,0x2000+alignment,data)
            result,new_trace=execute(source,0x102097f4,seed,0x2000+alignment,data)
            expected=zlib.crc32(data,seed^0xffffffff)^0xffffffff
            if original!=result or result!=expected or old_trace!=new_trace:raise ValueError('CRC result or read trace mismatch')
            cases+=1
    rows=[]
    stock_bytes=IMAGE.read_bytes()
    from verify_gx8002_analog_source import sha
    for section in placement['sections']:
        name=section['symbol'];offset=int(section['package_offset'],0)
        data=name.endswith('_table')
        rows.append({'symbol':name,'section_name':('.rodata.' if data else '.text.')+name,
                     'ownership_kind':'generated_source_data' if data else 'compiled_c',
                     'compiled_bytes':section['compiled_bytes'],'compiled_sha256':section['sha256'],
                     'stock_occurrences':[{'symbol':name,'package_offset':offset,'bytes':section['capacity'],
                     'sha256':sha(stock_bytes[offset:offset+section['capacity']]),'region':'image_a_xip_data' if data else 'image_a_xip_text'}]})
    report={'placement':placement,'functions':rows,'cases':cases,'exact_read_traces':True,'independent_zlib_oracle':True,'source_admitted':True,
            'limits':['Finite lengths and seeds; ordinary non-aliasing memory only.','No hardware timing or full CPU qualification.']}
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(verify(),indent=2))
