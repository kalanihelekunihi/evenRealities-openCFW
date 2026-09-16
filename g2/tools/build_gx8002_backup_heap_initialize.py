# SPDX-License-Identifier: MIT
"""Compile recovered allocator initialization at its original backup address."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    out=ROOT/'build/gx8002-backup-heap-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'heap.o')],check=True)
    (out/'heap.ld').write_text('SECTIONS { .heap_init 0x10009a44 : { *(.text*) } }\nbackup_heap_state = 0x200176dc;\nprintf = 0x10009934;\nbackup_heap_invalid_message = 0x100131d8;\nbackup_heap_initialize_message = 0x100131ac;\n')
    path=out/'heap.elf';subprocess.run([pre+'ld','-T',str(out/'heap.ld'),str(out/'heap.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'heap');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'heap.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    size=alloc[0]['size'];report={'source_sha256':sha(source.read_bytes()),'stock_sha256':sha(stock[0x42384:0x423f8]),'bytes':size,'envelope_bytes':116,'fits':size<=116,'source_admitted':False,'limits':['Recovered alignment checks and first/sentinel block setup. State and diagnostic strings external; decoded behavior and integration pending. No upstream version identity claimed.']}
    (ROOT/'docs/research/gx8002-backup-heap-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
