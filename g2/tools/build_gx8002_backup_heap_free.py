# SPDX-License-Identifier: MIT
"""Compile recovered free control flow without substituting the merger."""
import json,subprocess
from build_gx8002_backup_heap_initialize import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-heap-free';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_free.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # Stock shares the null-return epilogue; avoid a second shrink-wrapped exit.
    subprocess.run([pre+'gcc','-Os','-fno-shrink-wrap','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'free.o')],check=True)
    bindings={'backup_heap_state':0x200176dc,'printf':0x10009934,'backup_heap_merge':0x100099d4,'backup_heap_free_range':0x10013244,'backup_heap_free_invalid':0x10013254,'backup_heap_free_details':0x10013270}
    ld='SECTIONS { .free 0x10009c2c : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items())
    (out/'free.ld').write_text(ld);path=out/'free.elf';subprocess.run([pre+'ld','-T',str(out/'free.ld'),str(out/'free.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'free');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'free.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_backup_heap.h').read_bytes()),'bytes':alloc[0]['size'],'envelope_bytes':120,'fits':alloc[0]['size']<=120,'bindings':bindings,'source_admitted':False,'limits':['Invalid used/magic diagnostics do not prevent freeing, matching stock. Heap state is source-defined in the heap-data component; this standalone candidate binds it by address. Merger and diagnostics remain external. Decoded equivalence and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-heap-free.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
