# SPDX-License-Identifier: MIT
"""Build overlap-aware memory move; decoded qualification remains separate."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    out=ROOT/'build/gx8002-backup-memmove';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_memmove.c'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'memmove.o')],check=True)
    (out/'memmove.ld').write_text('SECTIONS { .text 0x10009968 : { *(.text.open_cfw_gx8002_memmove) } }\nopen_cfw_gx8002_memcpy = 0x10011344;\n')
    subprocess.run([pre+'ld','-T',str(out/'memmove.ld'),str(out/'memmove.o'),'-o',str(out/'memmove.elf')],check=True)
    elf=Elf32((out/'memmove.elf').read_bytes(),'memmove.elf');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unowned allocated section')
    if elf.relocations(section['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved source')
    (out/'memmove.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'memmove.elf')],text=True))
    return {'symbol':'open_cfw_gx8002_memmove','package_offset':0x422a8,'stock_envelope_bytes':40,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x422a8:0x422d0]),'source_sha256':sha(source.read_bytes()),'fits':len(payload)<=40,'source_admitted':False,'limits':['Forward branch calls separately reconstructed memcpy; overlap/ABI qualification pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-memmove-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
