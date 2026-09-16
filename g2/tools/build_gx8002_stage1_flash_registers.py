# SPDX-License-Identifier: MIT
"""Link source-built SPL flash register transfer routines at original entries."""
import json,subprocess
from build_gx8002_stage1_flash_read import build as reader,ROOT,Elf32,sha
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA


def build():
    evidence=reader();out=ROOT/'build/gx8002-stage1-flash-registers';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    (out/'registers.ld').write_text('''SECTIONS {
.read 0x10000edc : { *(.text.sflash_read_reg) }
.write 0x10000f5c : { *(.text.sflash_write_reg) }
/DISCARD/ : { *(.text*) *(.data*) *(.rodata*) }
}
''')
    path=out/'registers.elf';subprocess.run([pre+'ld','-T',str(out/'registers.ld'),str(ROOT/'build/gx8002-stage1-flash-read/global.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'registers');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,off in (('.read',0x39830),('.write',0x398b0)):
        section=next(s for s in elf.sections if s['name']==name);assert section['size']<=128
        rows.append({'name':name,'bytes':section['size'],'package_offset':off,'stock_byte_exact':elf.contents(section)==stock[off:off+section['size']]})
    (out/'registers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'reader_build':evidence,'sections':rows,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Complete source-built register transfer helpers fit original128-byte entries, no external dependencies. Decoded polling/transfer verification and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-stage1-flash-registers.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
