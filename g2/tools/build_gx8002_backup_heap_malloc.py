# SPDX-License-Identifier: MIT
"""Compile recovered backup first-fit allocation."""
import json,subprocess
from build_gx8002_backup_heap_initialize import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-heap-malloc';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_malloc.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-fno-shrink-wrap','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'malloc.o')],check=True)
    bindings={'backup_heap_state':0x200176dc,'printf':0x10009934,'backup_heap_malloc_align':0x10013214,'backup_heap_malloc_large':0x10013238}
    ld='SECTIONS { .malloc 0x10009ab8 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items())
    (out/'malloc.ld').write_text(ld);path=out/'malloc.elf';subprocess.run([pre+'ld','-T',str(out/'malloc.ld'),str(out/'malloc.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'free');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'malloc.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_backup_heap.h').read_bytes()),'bytes':alloc[0]['size'],'envelope_bytes':340,'fits':alloc[0]['size']<=340,'bindings':bindings,'source_admitted':False,'limits':['Recovered first-fit scan, split threshold, current/maximum usage accounting and lowest-free advancement. Decoded verification and integration pending; no upstream version identity claimed.']}
    (ROOT/'docs/research/gx8002-backup-heap-malloc.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
