#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile device labels, authenticated against stock references and SDK IDs."""
import json,shutil,struct,subprocess
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT

ROWS=[('p25q21l',0x153e0,0x854012),('p25q40l',0x153e8,0x856013),
      ('p25q80l',0x153f0,0x856014),('en25s20a',0x153f8,0x1c3812),
      ('en25s40a',0x15401,0x1c3813),('zb25wq80a',0x1540a,0x5e3414)]

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';relative='drivers_lib/mtd/spinor/spi_nor_ids.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    upstream=authenticated_blob(sdk/relative,blob);oracle=Elf32(upstream,relative)
    names=oracle.contents(next(s for s in oracle.sections if s['name']=='.rodata.str1.1'))
    out=ROOT/'build/gx8002-board';source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_device_names.c';obj=out/'flash-device-names.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    functions=[];oracle_offset=0
    for i,(name,offset,jedec) in enumerate(ROWS):
        symbol='open_cfw_gx8002_flash_name_'+name;section_name='.rodata.'+symbol
        sec=next(s for s in elf.sections if s['name']==section_name);payload=elf.contents(sec)
        if payload!=name.encode('ascii')+b'\0' or sec['align']!=1 or elf.relocations(sec['index']):raise ValueError('name layout')
        pointer,device_id=struct.unpack_from('<II',stock,0x18638+i*24)
        if pointer!=offset+0x101f6a74 or device_id!=jedec:raise ValueError('device reference')
        if payload!=stock[offset:offset+len(payload)] or payload!=names[oracle_offset:oracle_offset+len(payload)]:raise ValueError('name mismatch')
        oracle_offset+=len(payload)
        functions.append({'symbol':symbol,'section_name':section_name,'ownership_kind':'generated_source_data',
          'compiled_bytes':len(payload),'compiled_sha256':sha(payload),
          'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':len(payload),'sha256':sha(payload),'region':'image_a_xip_text'}]})
    if oracle_offset!=len(names):raise ValueError('unaccounted SDK names')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'flash-device-names.o')
    return {'functions':functions,'source_sha256':sha(source.read_bytes()),'flags':FLAGS,
            'sdk_commit':SDK_COMMIT,'sdk_object_git_blob':blob,'source_admitted':True,'hardware_qualified':False,
            'limits':['Six device labels only. Device descriptor word at offset12 remains unresolved; no claim of descriptor ownership or physical device qualification.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-device-names-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
