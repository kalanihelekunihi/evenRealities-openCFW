# SPDX-License-Identifier: MIT
"""Build event ingress using reviewed C and pinned upstream type definitions."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,IMAGE,IMAGE_SHA,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-trigger-app-event';out.mkdir(exist_ok=True);headers=[]
    for rel in ('lvp/app_core/lvp_app_core.h','lvp/app_core/lvp_app.h','lvp/common/lvp_queue.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();raw=authenticated_blob(sdk/rel,blob)
        (out/rel.split('/')[-1]).write_bytes(raw);headers.append({'path':rel,'blob':blob,'sha256':sha(raw)})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_trigger_app_event.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(out),'-c',str(source),'-o',str(out/'trigger.o')],check=True)
    (out/'trigger.ld').write_text('SECTIONS { .event_trigger 0x1000bde8 : { *(.text*) } }\nLvpQueuePut = 0x10015b64;\nopen_cfw_gx8002_app_event_queue = 0x2002d784;\n')
    path=out/'trigger.elf';subprocess.run([pre+'ld','-T',str(out/'trigger.ld'),str(out/'trigger.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trigger');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=elf.contents(sections[0]);assert len(body)<=20
    (out/'trigger.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'headers':headers,'sdk_commit':SDK_COMMIT,'source_sha256':sha(source.read_bytes()),'bytes':len(body),'envelope_bytes':20,'exact_stock':body==stock[0x44728:0x4473c],'source_admitted':False,'limits':['Queue failure intentionally ignored as stock does; callback/queue composition and hardware qualification separate.']}
    (ROOT/'docs/research/gx8002-backup-trigger-app-event.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
