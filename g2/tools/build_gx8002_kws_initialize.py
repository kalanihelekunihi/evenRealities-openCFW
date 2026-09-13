# SPDX-License-Identifier: MIT
"""Link recovered KWS initialize wrapper and require exact stock instructions."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    out=ROOT/'build/gx8002-kws-initialize';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_initialize.c'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'init.o')],check=True)
    (out/'init.ld').write_text('SECTIONS { .text 0x10206d90 : { *(.text.open_cfw_gx8002_kws_initialize) } }\nopen_cfw_gx8002_kws_flash_load = 0x10206cb0;\ngx_snpu_init = 0x10205cf4;\nopen_cfw_gx8002_kws_callback = 0x20027b50;\n')
    subprocess.run([pre+'ld','-T',str(out/'init.ld'),str(out/'init.o'),'-o',str(out/'init.elf')],check=True)
    elf=Elf32((out/'init.elf').read_bytes(),'init.elf');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if payload!=stock[0x1031c:0x10338]:raise ValueError('KWS initialization exact match')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unowned section')
    (out/'init.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'init.elf')],text=True))
    return {'symbol':'open_cfw_gx8002_kws_initialize','section_name':'.text','package_offset':0x1031c,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x1031c:0x10338]),'source_sha256':sha(source.read_bytes()),'exact_stock_match':True,'source_admitted':False,'limits':['Exact wrapper match; helper composition and source-admission export pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-kws-initialize-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Exact28-byte stock match')
