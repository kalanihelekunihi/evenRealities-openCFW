#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the pinned-upstream main adaptation using the native macOS compiler."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'LvpSystemInit':0x102078a4,'LvpInitMode':0x102085a4,'LvpInitializeAppEvent':0x10208cd4,'LvpModeTick':0x102085f8,'LvpSystemDone':0x10207a7c,'LvpAppEventTick':0x10208d48}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/main.c','lvp/lvp_mode.h','lvp/app_core/lvp_app_core.h','lvp/common/lvp_system_init.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_main.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(sdk/'lvp'),'-c',str(source),'-o',str(out/'main-candidate.o')],check=True)
    script=out/'main-candidate.ld';script.write_text('SECTIONS { .text 0x10026314 : { *(.text.open_cfw_gx8002_main) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'main-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'main-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));s=next(x for x in e.sections if x['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if e.relocations(s['index']) or any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved main')
    (out/'main-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),
            'compiled_bytes':s['size'],'compiled_sha256':sha(e.contents(s)),'package_offset':0x18328,
            'stock_envelope_bytes':44,'stock_sha256':sha(stock[0x18328:0x18354]),'fits':s['size']<=44,
            'source_admitted':False,'limits':['Adapted TWS mode main; system and mode dependencies require separate reconstruction.']}
    (ROOT/'docs/research/gx8002-main-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
