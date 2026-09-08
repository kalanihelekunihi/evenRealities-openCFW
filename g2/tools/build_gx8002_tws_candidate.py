#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a TWS initialization candidate; no source admission without comparison."""
import json,subprocess,re
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'LvpQueueInit':0x10206f9c,'LvpInitMaxKws':0x10208944,'gx_pmu_get_wakeup_source':0x10024940,
'LvpKwsInit':0x10206d90,'LvpAudioInInit':0x102073bc,'LvpAudioInStandbyToStartup':0x10207660,'printf':0x10206c24,
'open_cfw_gx8002_tws_snpu_callback':0x10026340,'open_cfw_gx8002_tws_audio_callback':0x100263dc,
'open_cfw_gx8002_tws_init_error':0x1020b230,'open_cfw_gx8002_tws_state':0x2002e6ec}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/lvp_mode_tws.c','lvp/lvp_mode.h','lvp/common/lvp_queue.h','include/driver/gx_snpu.h','include/driver/gx_pmu_ctrl.h','lvp/common/lvp_audio_in.h','lvp/common/snpu_engine/lvp_kws.h','lvp/vui/kws/max_decoder.c','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    config=out/'tws-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_tws_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    # Compile exact authenticated interface excerpts with the recovered declarations.
    # This probe is type evidence only and never contributes firmware bytes.
    pmu=(sdk/'include/driver/gx_pmu_ctrl.h').read_text()
    audio=(sdk/'lvp/common/lvp_audio_in.h').read_text()
    kws=(sdk/'lvp/common/snpu_engine/lvp_kws.h').read_text()
    patterns=[(pmu,r'typedef enum \{[^}]*\} GX_WAKEUP_SOURCE;'),
              (pmu,r'GX_WAKEUP_SOURCE gx_pmu_get_wakeup_source\(void\);'),
              (audio,r'typedef int \(\*AUDIO_IN_RECORD_CALLBACK\)\(int ctx_index, void \*priv\);'),
              (audio,r'int LvpAudioInInit\(AUDIO_IN_RECORD_CALLBACK callback\);'),
              (audio,r'void LvpAudioInStandbyToStartup\(void\);'),
              (kws,r'int LvpKwsInit\(GX_SNPU_CALLBACK callback, GX_WAKEUP_SOURCE start_mode\);')]
    excerpts=[]
    for text,pattern in patterns:
        matches=re.findall(pattern,text)
        if len(matches)!=1:raise ValueError('TWS interface excerpt changed')
        excerpts.append(matches[0])
    interfaces=config/'tws-upstream-interfaces.h'
    interfaces.write_text('/* Exact declarations from authenticated upstream source headers. */\n'+'\n'.join(excerpts)+'\n')
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'lvp'),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'tws-candidate.o')],check=True)
    probe=out/'tws-interface-probe.c'
    probe.write_text('#include "'+str(source)+'"\n'
        '_Static_assert(__builtin_types_compatible_p(GX_WAKEUP_SOURCE, unsigned int), "wakeup compatibility");\n'
        '_Static_assert(GX_WAKEUP_SOURCE_COLD == 0 && GX_WAKEUP_SOURCE_WDT == 1, "reset values");\n')
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'lvp'),'-I'+str(sdk/'include'),'-fsyntax-only',str(probe)],check=True)
    script=out/'tws-candidate.ld';script.write_text('SECTIONS { .text 0x10208670 : { *(.text.open_cfw_gx8002_tws_init) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'tws-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'tws-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('TWS stock/link invariant')
    (out/'tws-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),
    'interface_header_sha256':sha(interfaces.read_bytes()),'interface_probe_sha256':sha(probe.read_bytes()),'interface_compatibility_checked':True,
    'config_sha256':sha((config/'autoconf.h').read_bytes()),'compiled_bytes':sec['size'],'compiled_sha256':sha(e.contents(sec)),
    'package_offset':0x11bfc,'stock_envelope_bytes':108,'stock_sha256':sha(stock[0x11bfc:0x11c68]),'fits':sec['size']<=108,
    'source_admitted':False,'limits':['Candidate only. Need continuous stock/source call and state comparison, stack/ABI checks, and interface type compatibility verification before admission.']}
    (ROOT/'docs/research/gx8002-tws-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
