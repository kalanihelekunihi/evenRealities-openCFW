#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Place source CRC code and generated table; not execution qualification."""
import json
import subprocess
from pathlib import Path
from generate_gx8002_crc_table import generate
from verify_gx8002_analog_source import FLAGS, sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32
ROOT=Path(__file__).resolve().parents[1]
SCRIPT='''SECTIONS {
 .text.open_cfw_gx8002_crc32_no_comp 0x102097f4 : { *(.text.open_cfw_gx8002_crc32_no_comp) }
 .text.open_cfw_gx8002_crc32 0x102098a8 : { *(.text.open_cfw_gx8002_crc32) }
 .rodata.open_cfw_gx8002_crc_table 0x1020b908 : { *(.rodata.open_cfw_gx8002_crc_table) }
 /DISCARD/ : { *(.comment) *(.note*) }
}
'''

def main(prefix=None, output=None):
    output=output or ROOT/'build/gx8002-crc-linked';output.mkdir(parents=True,exist_ok=True)
    table=generate(output)
    prefix=prefix or ROOT/'build/csky-macos/install/bin'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_crc32.c'
    flags=[*FLAGS,'-fno-tree-loop-optimize']
    for src,name in ((source,'crc'),(output/'crc_table.c','table')):
        subprocess.run([str(prefix/'csky-unknown-elf-gcc'),*flags,'-c',str(src),'-o',str(output/(name+'.o'))],check=True)
    (output/'crc.ld').write_text(SCRIPT)
    linked=output/'crc.elf'
    subprocess.run([str(prefix/'csky-unknown-elf-ld'),'-T',str(output/'crc.ld'),str(output/'crc.o'),str(output/'table.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved symbol')
    expected_sections={'.text.open_cfw_gx8002_crc32_no_comp', '.text.open_cfw_gx8002_crc32', '.rodata.open_cfw_gx8002_crc_table'}
    if {s['name'] for s in elf.sections if s['flags'] & 2 and s['size']} != expected_sections:
        raise ValueError('unexpected allocated section')
    rows=[]
    for name,offset,capacity in [('open_cfw_gx8002_crc32_no_comp',0x12d80,180),('open_cfw_gx8002_crc32',0x12e34,12),('open_cfw_gx8002_crc_table',0x14e94,1024)]:
        section=next(s for s in elf.sections if s['name'].endswith('.'+name));payload=elf.contents(section)
        if section['address'] != offset + 0x101f6a74:
            raise ValueError('unexpected runtime placement')
        if len(payload)>capacity or elf.relocations(section['index']):raise ValueError('placement failed')
        exact=payload==stock[offset:offset+capacity]
        if name!='open_cfw_gx8002_crc32_no_comp' and not exact:raise ValueError('wrapper/table not exact')
        rows.append({'symbol':name,'package_offset':hex(offset),'capacity':capacity,'compiled_bytes':len(payload),'sha256':sha(payload),'byte_exact':exact})
    report={'source_sha256':sha(source.read_bytes()),'table_generator_sha256':table['generator_sha256'],'linker_script_sha256':sha(SCRIPT.encode()),'flags':flags,'sections':rows,'source_admitted':False,'limits':['Placement only; CRC core instruction comparison still pending.','No firmware container emitted.']}
    (output/'placement.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(main(),indent=2))
