#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed Timer callback dispatch call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_clock_time_us':0x10005070}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-timer-dispatch';out.mkdir(exist_ok=True);rel='arch/soc/grus/spl/spl_counter.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_clock.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'timer-dispatch-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_timer_dispatch.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-jump-tables','-fno-ivopts']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'timer-dispatch-candidate.o')],check=True)
    script=out/'timer-dispatch-candidate.ld';script.write_text('SECTIONS { .text 0x100050cc : { *(.text.open_cfw_gx8002_timer_dispatch) } .timer_state 0x200174bc (NOLOAD) : { *(.bss.open_cfw_timer_slots) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'timer-dispatch-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'timer-dispatch-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('Timer callback dispatch stock/link')
    (out/'timer-dispatch-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'counter_subsystem_reference_only; dispatch recovered from stock'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_timer_dispatch','section_name':'.text','package_offset':0x3da0c,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':120,'stock_sha256':sha(stock[0x3da0c:0x3da84]),'fits':len(payload)<=120,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    state=next(s for s in e.sections if s['name']=='.timer_state')
    if state['type']!=8 or state['address']!=0x200174bc or state['size']!=360 or state['flags']&4:raise ValueError('Timer BSS layout')
    assert 0x20017090 <= state['address'] and state['address']+state['size']<=0x2002d79c
    (ROOT/'docs/research/gx8002-backup-timer-dispatch-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
