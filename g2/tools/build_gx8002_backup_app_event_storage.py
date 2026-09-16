# SPDX-License-Identifier: MIT
"""Build event queue BSS from pinned SDK types and observed initializer geometry."""
import json,subprocess
from build_gx8002_backup_app_event_tick import build as tick_build,ROOT,Elf32,sha


def build():
    evidence=tick_build();headers=ROOT/'build/gx8002-backup-app-event-tick'
    out=ROOT/'build/gx8002-backup-app-event-storage';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_app_event_storage.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-common','-fdata-sections','-I',str(headers),'-c',str(source),'-o',str(out/'storage.o')]
    subprocess.run(command,check=True)
    script='SECTIONS { .app_event_buffer 0x2002d31c (NOLOAD) : { *(.bss.s_app_misc_event_queue_buffer) } .app_event_queue 0x2002d784 (NOLOAD) : { *(.bss.s_app_misc_event_queue) } }\n'
    (out/'storage.ld').write_text(script);path=out/'storage.elf';subprocess.run([pre+'ld','-T',str(out/'storage.ld'),str(out/'storage.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'events');rows=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert [(s['address'],s['size'],s['type']) for s in rows]==[(0x2002d31c,64,8),(0x2002d784,20,8)]
    assert all(0x20017090<=s['address'] and s['address']+s['size']<=0x2002d79c for s in rows)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    result={'upstream_type_evidence':evidence['upstream_files'],'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':84,'source_admitted':False,'limits':['Storage types and offsets compile-time checked; geometry matches stock initializer arguments. Both BSS objects lie in reset clear interval.', 'Event initialization and queue lifetime/concurrency remain separately unqualified.']}
    (ROOT/'docs/research/gx8002-backup-app-event-storage.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['bytes'])
