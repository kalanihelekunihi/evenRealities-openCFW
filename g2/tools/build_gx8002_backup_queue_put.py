# SPDX-License-Identifier: MIT
"""Identify and build pinned SDK queue insertion at the backup entry."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-queue-put';out.mkdir(exist_ok=True)
    records=[]
    for rel in ('lvp/common/lvp_queue.c','lvp/common/lvp_queue.h','include/lvp_attr.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);records.append({'path':rel,'blob':blob,'sha256':sha(data)})
        if rel.endswith('.c'):data=data.replace(b'#include <stdio.h>\n',b'')
        (out/rel.split('/')[-1]).write_bytes(data)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-fno-ivopts','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-I',str(out),'-c',str(ROOT/'components/shared/gx8002/runtime_gx8002_backup_queue_put.c'),'-o',str(out/'queue.o')]
    subprocess.run(command,check=True)
    (out/'queue.ld').write_text('SECTIONS { .queue_put 0x10015b64 : { *(.text.LvpQueuePut) } /DISCARD/ : { *(.text*) *(.sram_text*) } }\n')
    path=out/'queue.elf';subprocess.run([pre+'ld','-T',str(out/'queue.ld'),str(out/'queue.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'queue');section=next(s for s in elf.sections if s['name']=='.queue_put');body=elf.contents(section)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    exact=body==stock[0x4e4a4:0x4e4a4+len(body)]
    (out/'queue.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_backup_queue_put.c').read_bytes()),'sdk_commit':SDK_COMMIT,'upstream_files':records,'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':len(body),'envelope_bytes':100,'fits':len(body)<=100,'stock_byte_exact':exact,'source_admitted':False,'limits':['Backup-specific C preserves observed queue metadata-read order using the authenticated SDK layout.', 'Zero record size and signed division exception behavior remain outside qualification; caller contracts and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-backup-queue-put.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
