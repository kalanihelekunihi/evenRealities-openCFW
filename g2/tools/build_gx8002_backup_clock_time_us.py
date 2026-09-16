# SPDX-License-Identifier: MIT
"""Place the reconstructed microsecond counter in backup firmware."""
import json, subprocess
from build_gx8002_clock_time_us_candidate import build as original_build, ROOT, Elf32, sha


def build():
    evidence=original_build();out=ROOT/'build/gx8002-backup-clock-time-us';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'timer.o';obj.write_bytes((ROOT/'build/gx8002-board/clock-time-us-candidate.o').read_bytes())
    (out/'timer.ld').write_text('SECTIONS { .timer 0x10005070 : { *(.text*) } }\n')
    path=out/'timer.elf';subprocess.run([pre+'ld','-T',str(out/'timer.ld'),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup timer');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.timer'
    assert sections[0]['size']<=92
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'timer.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'elf_sha256':sha(path.read_bytes()),'bytes':sections[0]['size'],'envelope_bytes':92,'fits':True,'source_admitted':False,'limits':['Low word then high word snapshot; modulo-64 scaling. Hardware counter coherence remains unqualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-time-us.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['bytes'])
