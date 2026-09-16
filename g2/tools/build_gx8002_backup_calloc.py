# SPDX-License-Identifier: MIT
"""Compile recovered RT calloc with explicit allocation dependency."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    out=ROOT/'build/gx8002-backup-calloc';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_calloc.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'calloc.o')],check=True)
    (out/'calloc.ld').write_text('SECTIONS { .calloc 0x10009c0c : { *(.text*) } }\nrt_malloc = 0x10009ab8;\nmemset = 0x100113c4;\n')
    path=out/'calloc.elf';subprocess.run([pre+'ld','-T',str(out/'calloc.ld'),str(out/'calloc.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'calloc');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==1
    body=elf.contents(alloc[0]);assert len(body)<=32 and body==stock[0x4254c:0x4254c+len(body)]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(body),'stock_prefix_exact':True,'source_admitted':False,'limits':['Preserves stock unsigned multiplication wrap. Allocation remains external; no allocation-overflow fix claimed. Full allocator execution and hardware pending.']}
    (ROOT/'docs/research/gx8002-backup-calloc.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
