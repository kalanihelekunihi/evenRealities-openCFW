#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the named flash state fields and qualify their target layout."""
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
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.c'
    obj=out/'flash-state.o'
    subprocess.run([str(pre)+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    compatibility=out/'state-compatibility.c'
    modules=['state','discover','word_io','info','otp_region','initialize']
    compatibility.write_text(''.join('#include "'+str(ROOT/f'components/shared/gx8002/runtime_gx8002_flash_{name}.c')+'"\n' for name in modules))
    subprocess.run([str(pre)+'gcc',*FLAGS,'-fsyntax-only',str(compatibility)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));name='.data.open_cfw_gx8002_flash_state'
    section=next(s for s in elf.sections if s['name']==name)
    payload=elf.contents(section)
    fields={'device_index':-1,'usable_bytes':0,'address_bytes':0,'selected_device':0,'command':[0]*8,'program_words':0,'read_words':0}
    if payload!=struct.pack('<8I',0xffffffff,0,0,0,0,0,0,0) or section['align']!=4 or elf.relocations(section['index']):raise ValueError('flash state target layout mismatch')
    stock=IMAGE.read_bytes();offset=0x184f8
    if sha(stock)!=IMAGE_SHA or stock[offset:offset+32]!=payload:raise ValueError('flash state stock mismatch')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'flash-state.o')
    return {'functions':[{'symbol':'open_cfw_gx8002_flash_state','section_name':name,
            'ownership_kind':'generated_source_data','compiled_bytes':32,'compiled_sha256':sha(payload),
            'stock_occurrences':[{'symbol':'flash_state','package_offset':offset,'bytes':32,'sha256':sha(payload),'region':'image_a_sram_data'}]}],
            'state_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':FLAGS,'fields':fields,
            'evidence':['Discovery owns index/size/address-width/device; OTP paths use command scratch bytes.',
                        'Initializer installs word-program/read callbacks at offsets 24/28.'],
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Matches shipped initial state; interface/device ownership and physical startup remain unqualified.']}

if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-state-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
