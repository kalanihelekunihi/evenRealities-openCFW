# SPDX-License-Identifier: MIT
"""Authenticate fixed-control function pointers and upstream callback slots."""
import json,struct,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def analyze():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Fixed dispatch stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);elf=Elf32(data,rel)
    section=next(s for s in elf.sections if s['name']=='.data');relocations=elf.relocations(section['index']);symbols=elf.symbols();rows=[]
    for name,slot,address in (('aout_set_fixed_src',0x4c,0x10204cdc),('aout_get_sdc_addr',0x50,0x10204cfc)):
        relocation=next(r for r in relocations if r['offset']==0x34+slot)
        symbol=symbols[relocation['symbol']]
        target=elf.sections[symbol['section']]['name']
        if relocation['type']!=1 or target!='.text.'+name:raise ValueError('Callback relocation mismatch')
        offset=0x18bdc+slot
        if struct.unpack_from('<I',stock,offset)[0]!=address:raise ValueError('Stock callback slot mismatch')
        rows.append({'symbol':name,'slot':slot,'stock_pointer_offset':offset,'runtime_target':address,'upstream_relocation':relocation})
    if struct.unpack_from('<I',stock,0xeaf4)[0]!=0x20026bc8:raise ValueError('Stock table literal mismatch')
    return {'stock_sha256':IMAGE_SHA,'sdk_commit':SDK_COMMIT,'upstream_blob':blob,'upstream_path':rel,'callbacks':rows,'stock_table_package_offset':0x18bdc,'stock_table_runtime_address':0x20026bc8,'table_address_literal_offset':0xeaf4,'limits':['Stock callback values agree with authenticated upstream slot layout. Literal occurrence is address evidence, not complete runtime dispatch execution.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-audio-output-fixed-dispatch.json').write_text(json.dumps(r,indent=2)+'\n');print('Two stock callback slots authenticated')
