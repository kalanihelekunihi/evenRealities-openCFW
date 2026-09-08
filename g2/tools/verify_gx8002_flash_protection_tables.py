#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the named OTP configuration fields and qualify their target layout."""
import json
import shutil
import struct
import subprocess
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_protection_tables.c'
    obj=out/'protection-tables.o'
    subprocess.run([str(pre)+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    functions=[]
    for capacity,offset,count in [(256,0x18590,5),(512,0x185b8,7),(1024,0x185f0,9)]:
        symbol=f'open_cfw_gx8002_flash_protection_{capacity}k'
        name='.rodata.'+symbol;section=next(s for s in elf.sections if s['name']==name)
        payload=elf.contents(section)
        if len(payload)!=count*8 or section['align']!=4 or elf.relocations(section['index']):raise ValueError('protection table layout')
        if payload!=stock[offset:offset+count*8]:raise ValueError('protection policy mismatch')
        lengths=[struct.unpack_from('<I',payload,i*8+4)[0] for i in range(count)]
        if lengths!=sorted(set(lengths)) or lengths[0]!=0 or lengths[-1]!=capacity*1024:raise ValueError('protection length ordering')
        functions.append({'symbol':symbol,'section_name':name,'ownership_kind':'generated_source_data',
          'compiled_bytes':len(payload),'compiled_sha256':sha(payload),
          'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':len(payload),'sha256':sha(payload),'region':'image_a_sram_data'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'protection-tables.o')
    return {'functions':functions,'table_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_protection_tables.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':FLAGS,
      'source_admitted':True,'hardware_qualified':False,
      'evidence':['Source-built protection query/setter establish four status bytes and protected length per entry.',
                  'Initializer at package0x166d8 establishes table pointers/counts5/7/9.'],
      'limits':['Policy matches shipped firmware; vendor register semantics and physical protection not independently qualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-protection-tables-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
