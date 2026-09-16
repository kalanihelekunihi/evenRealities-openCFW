# SPDX-License-Identifier: MIT
"""Compile shared flash type getter at its backup callback address."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    out=ROOT/'build/gx8002-backup-flash-gettype';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_info.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'info.o')],check=True)
    subprocess.run([pre+'objcopy','--localize-symbol=open_cfw_gx8002_flash_getinfo',str(out/'info.o')],check=True)
    (out/'info.ld').write_text('SECTIONS { .flash_gettype 0x10007f58 : { *(.text.open_cfw_gx8002_flash_gettype) } /DISCARD/ : { *(.text.open_cfw_gx8002_flash_getinfo) *(.rodata*) } }\nopen_cfw_gx8002_flash_state = 0x20016d60;\n')
    path=out/'info.elf';subprocess.run([pre+'ld','-T',str(out/'info.ld'),str(out/'info.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'type');sec=next(s for s in elf.sections if s['name']=='.flash_gettype');stock=IMAGE.read_bytes();payload=elf.contents(sec)
    assert sha(stock)==IMAGE_SHA and payload==stock[0x40898:0x408a4] and sec['address']==0x10007f58 and not elf.relocations(sec['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'info.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_flash_state.h').read_bytes()),'compiled_bytes':12,'compiled_sha256':sha(payload),'byte_exact':True,'source_admitted':False,'hardware_qualified':False,'limits':['Selected device pointer ownership remains dependent on flash discovery. Getter preserves unchecked dereference behavior.']}
    (ROOT/'docs/research/gx8002-backup-flash-gettype.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
