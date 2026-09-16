# SPDX-License-Identifier: MIT
"""Compile recovered backup reallocation."""
import json,subprocess
from build_gx8002_backup_heap_initialize import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-heap-realloc';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_realloc.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-fno-tree-ter','-fno-tree-coalesce-vars','-fno-shrink-wrap','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'realloc.o')],check=True)
    bindings={'backup_heap_state':0x200176dc,'printf':0x10009934,'backup_heap_realloc_large':0x100132a0,'rt_malloc':0x10009ab8,'rt_free':0x10009c2c,'backup_heap_merge':0x100099d4,'memcpy':0x10011344}
    ld='SECTIONS { .realloc 0x10009ca4 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items())
    (out/'realloc.ld').write_text(ld);path=out/'realloc.elf';subprocess.run([pre+'ld','-T',str(out/'realloc.ld'),str(out/'realloc.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'realloc');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'realloc.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_backup_heap.h').read_bytes()),'bytes':alloc[0]['size'],'envelope_bytes':216,'fits':alloc[0]['size']<=216,'bindings':bindings,'source_admitted':False,'limits':['Recovered alignment, range handling, strict shrink threshold, split repair, allocation failure and copy/free behavior. Decoded verification and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-heap-realloc.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
