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
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_descriptor.c'
    obj=out/'otp-descriptor.o'
    subprocess.run([str(pre)+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));name='.data.open_cfw_gx8002_flash_otp_descriptor'
    section=next(s for s in elf.sections if s['name']==name)
    payload=elf.contents(section)
    fields={'base_address':4096,'region_stride':4096,'region_bytes':512,'region_count':3,'selection_flags':0}
    if payload!=struct.pack('<5I',*fields.values()) or section['align']!=4 or elf.relocations(section['index']):raise ValueError('OTP descriptor target layout mismatch')
    stock=IMAGE.read_bytes();offset=0x186e0
    if sha(stock)!=IMAGE_SHA or stock[offset:offset+20]!=payload:raise ValueError('OTP descriptor stock mismatch')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'otp-descriptor.o')
    return {'functions':[{'symbol':'open_cfw_gx8002_flash_otp_descriptor','section_name':name,
            'ownership_kind':'generated_source_data','compiled_bytes':20,'compiled_sha256':sha(payload),
            'stock_occurrences':[{'symbol':'flash_otp_descriptor','package_offset':offset,'bytes':20,'sha256':sha(payload),'region':'image_a_sram_data'}]}],
            'source_sha256':sha(source.read_bytes()),'flags':FLAGS,'fields':fields,
            'evidence':['OTP read at package 0x15fb8: base+offset+selected_region*stride.',
                        'Qualified region accessors establish size/count/selection flags at offsets 8/12/16.'],
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Matches shipped descriptor configuration; physical OTP behavior remains unqualified.']}

if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-otp-descriptor-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
