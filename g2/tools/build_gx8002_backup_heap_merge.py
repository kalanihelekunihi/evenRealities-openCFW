# SPDX-License-Identifier: MIT
"""Compile recovered adjacent-free-block coalescing."""
import json,subprocess
from build_gx8002_backup_heap_initialize import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-heap-merge';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_merge.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'merge.o')],check=True)
    bindings={'backup_heap_state':0x200176dc}
    ld='SECTIONS { .merge 0x100099d4 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items())
    (out/'merge.ld').write_text(ld);path=out/'merge.elf';subprocess.run([pre+'ld','-T',str(out/'merge.ld'),str(out/'merge.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'merge');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'merge.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_backup_heap.h').read_bytes()),'bytes':alloc[0]['size'],'envelope_bytes':112,'fits':alloc[0]['size']<=112,'bindings':bindings,'source_admitted':False,'limits':['Recovered forward and backward coalescing, including lowest-free updates and repeated volatile header reads. Decoded equivalence and integration pending. No upstream version identity claimed.']}
    (ROOT/'docs/research/gx8002-backup-heap-merge.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
