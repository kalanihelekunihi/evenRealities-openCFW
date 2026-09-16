# SPDX-License-Identifier: MIT
"""Identify and build pinned SDK queue extraction at the backup entry."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-queue-get';out.mkdir(exist_ok=True)
    records=[]
    for rel in ('lvp/common/lvp_queue.c','lvp/common/lvp_queue.h','include/lvp_attr.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);records.append({'path':rel,'blob':blob,'sha256':sha(data)})
        if rel.endswith('.c'):data=data.replace(b'#include <stdio.h>\n',b'')
        (out/rel.split('/')[-1]).write_bytes(data)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-I',str(out),'-c',str(out/'lvp_queue.c'),'-o',str(out/'queue.o')]
    subprocess.run(command,check=True)
    (out/'queue.ld').write_text('SECTIONS { .queue_get 0x10009fbc : { *(.text.LvpQueueGet) } /DISCARD/ : { *(.text*) *(.sram_text*) } }\nASSERT(SIZEOF(.queue_get) <= 80, "queue initializer overflow")\n')
    path=out/'queue.elf';subprocess.run([pre+'ld','-T',str(out/'queue.ld'),str(out/'queue.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'queue');section=next(s for s in elf.sections if s['name']=='.queue_get');body=elf.contents(section)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    exact=body==stock[0x428fc:0x428fc+len(body)]
    (out/'queue.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'upstream_files':records,'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':len(body),'stock_byte_exact':exact,'source_admitted':False,'limits':['Unused stdio include removed; complete SDK queue reader selected. Other queue operations remain out of this component.', 'Zero record size and signed division exception behavior remain outside qualification; caller contracts and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-backup-queue-get.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
