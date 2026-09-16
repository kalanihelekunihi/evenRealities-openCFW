# SPDX-License-Identifier: MIT
"""Compile authenticated denoise-mode main with explicit subsystem bindings."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    out=ROOT/'build/gx8002-backup-main';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';evidence=[]
    for rel,target in (('lvp/main.c','main.c'),('include/lvp_attr.h','lvp_attr.h'),('lvp/lvp_mode.h','lvp_mode.h'),('lvp/common/lvp_system_init.h','lvp_system_init.h'),('lvp/app_core/lvp_app_core.h','app_core/lvp_app_core.h')):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        raw=authenticated_blob(sdk/rel,blob);adapted=raw.replace(b'#include <stdio.h>\n',b'')
        path=out/target;path.parent.mkdir(exist_ok=True);path.write_bytes(adapted)
        evidence.append({'path':rel,'blob':blob,'sha256':sha(raw),'build_sha256':sha(adapted)})
    (out/'autoconf.h').write_text('#define CONFIG_LVP_INIT_WORKMODE_DENOISE 1\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-I',str(out),'-c',str(out/'main.c'),'-o',str(out/'main.o')],check=True)
    bindings={'LvpSystemInit':0x4322c,'LvpInitMode':0x44088,'LvpInitializeAppEvent':0x4473c,'LvpModeTick':0x440e0,'LvpSystemDone':0x4340c,'LvpAppEventTick':0x4479c}
    ld='SECTIONS { .main 0x10015cfc : { *(.sram_text) } }\n'+''.join(f'{name} = {offset-0x38940+0x10000000:#x};\n' for name,offset in bindings.items())
    (out/'main.ld').write_text(ld);path=out/'main.elf'
    subprocess.run([pre+'ld','-T',str(out/'main.ld'),str(out/'main.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup main');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.main'
    body=elf.contents(sections[0]);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert len(body)==40 and body==stock[0x4e63c:0x4e664]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'main.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_commit':SDK_COMMIT,'sources':evidence,'compiled_bytes':len(body),'envelope_bytes':40,'exact_stock_prefix':body==stock[0x4e63c:0x4e63c+len(body)],'bindings_package_offsets':bindings,'source_admitted':False,'limits':['Denoise mode selected; unused stdio include removed. Six subsystem bodies remain explicit dependencies. Full behavior and firmware admission pending.']}
    (ROOT/'docs/research/gx8002-backup-main.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
