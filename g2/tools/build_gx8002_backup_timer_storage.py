# SPDX-License-Identifier: MIT
"""Allocate recovered timer-slot state from C declarations."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32


def build():
    out=ROOT/'build/gx8002-backup-timer-storage';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_timer_dispatch.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-common','-fdata-sections','-ffunction-sections','-c',str(source),'-o',str(out/'storage.o')]
    subprocess.run(command,check=True)
    script='SECTIONS { .timer_slots 0x200174bc (NOLOAD) : { *(.bss.open_cfw_timer_slots) } /DISCARD/ : { *(.text*) } }\n'
    (out/'storage.ld').write_text(script);path=out/'storage.elf'
    subprocess.run([pre+'ld','-T',str(out/'storage.ld'),str(out/'storage.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'IRQ storage')
    rows=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert [(s['name'],s['address'],s['size'],s['type']) for s in rows]==[('.timer_slots',0x200174bc,360,8)]
    assert all(0x20017090<=s['address'] and s['address']+s['size']<=0x2002d79c for s in rows)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':360,'source_admitted':False,'limits':['C NOBITS storage with compile-time entry width/offset assertions. Placement lies inside recovered reset BSS-clear interval.', 'Timer callback lifecycle and full firmware admission remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-timer-storage.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
