# SPDX-License-Identifier: MIT
"""Compile pinned SDK application-event tick with recovered feature selection."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from build_gx8002_backup_queue_get import build as queue_build


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-app-event-tick';out.mkdir(exist_ok=True)
    records=[];texts={}
    for rel in ('lvp/app_core/lvp_app_core.c','lvp/app_core/lvp_app_core.h','lvp/app_core/lvp_app.h','lvp/common/lvp_queue.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);records.append({'path':rel,'blob':blob,'sha256':sha(data)});texts[rel]=data.decode()
        if rel.endswith('.h'):(out/rel.split('/')[-1]).write_bytes(data)
    text=texts['lvp/app_core/lvp_app_core.c'];start=text.index('int LvpAppEventTick(void)');brace=text.index('{',start);end=brace+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    source='#include "lvp_app.h"\n#include "lvp_queue.h"\nextern LVP_APP *app_core_ops;\nextern LVP_QUEUE s_app_misc_event_queue;\nextern int UartMessageAsyncTick(void);\n#define CONFIG_LVP_HAS_UART_MESSAGE_2_0 1\n'+text[start:end]+'\n'
    (out/'tick.c').write_text(source)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-I',str(out),'-c',str(out/'tick.c'),'-o',str(out/'tick.o')]
    subprocess.run(command,check=True)
    script='SECTIONS { .event_tick 0x1000be5c : { *(.text*) } }\nLvpQueueGet = 0x10009fbc;\ns_app_misc_event_queue = 0x2002d784;\napp_core_ops = 0x20016f74;\nUartMessageAsyncTick = 0x1000b4c8;\nASSERT(SIZEOF(.event_tick) <= 76, "event tick overflow")\n'
    queue_evidence=queue_build();queue=ROOT/'build/gx8002-backup-queue-get'
    script=script.replace('LvpQueueGet = 0x10009fbc;','').replace('*(.text*)',str(out/'tick.o')+'(.text*)')
    script=(queue/'queue.ld').read_text().replace('*(',str(queue/'queue.o')+'(')+script
    (out/'tick.ld').write_text(script);path=out/'tick.elf';subprocess.run([pre+'ld','-T',str(out/'tick.ld'),str(out/'tick.o'),str(queue/'queue.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'tick');sec=next(s for s in elf.sections if s['name']=='.event_tick');body=elf.contents(sec)
    prior=Elf32((queue/'queue.elf').read_bytes(),'queue');a=next(s for s in prior.sections if s['name']=='.queue_get');b=next(s for s in elf.sections if s['name']=='.queue_get')
    assert a['address']==b['address'] and prior.contents(a)==elf.contents(b)
    assert next(s for s in elf.symbols() if s['name']=='LvpQueueGet')['section'] not in (0,0xfff1)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'tick.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'queue_build':queue_evidence,'sdk_commit':SDK_COMMIT,'upstream_files':records,'derived_source_sha256':sha(source.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':len(body),'stock_byte_exact':body==stock[0x4479c:0x4479c+len(body)],'source_admitted':False,'limits':['SDK function body isolated unchanged; UART async tick enabled to match observed stock call. Queue reader is source-linked; app pointer and async helper remain external in this candidate.', 'Decoded callback mutation/queue behavior and integration remain pending.']}
    (ROOT/'docs/research/gx8002-backup-app-event-tick.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
