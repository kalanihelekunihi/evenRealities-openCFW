#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed flash probe retry wrapper; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'gx_clock_get_time_us':0x1002585c,'open_cfw_gx8002_flash_probe_callback':0x20026504}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_flash.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'flash-probe-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_probe.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fira-algorithm=priority']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'flash-probe-candidate.o')],check=True)
    script=out/'flash-probe-candidate.ld';script.write_text('SECTIONS { .text 0x1002475c : { *(.text.open_cfw_gx8002_flash_probe) } .probe_state 0x20026ff4 (NOLOAD) : { *(.bss.open_cfw_gx8002_flash_probe_state) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'flash-probe-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'flash-probe-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('analog voltage stock/link')
    (out/'flash-probe-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'board_call_site_reference_only; implementation recovered from stock'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_flash_probe','section_name':'.text','package_offset':0x16770,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':92,'stock_sha256':sha(stock[0x16770:0x167cc]),'fits':len(payload)<=92,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    state=next(x for x in e.sections if x['name']=='.probe_state')
    assert state['type']==8 and state['size']==1 and state['address']==0x20026ff4 and state['flags']==3
    clear=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());interval=clear['evidence']['build']
    assert interval['bss_start']<=state['address']<state['address']+1<=interval['bss_end']
    clear_path=ROOT/'build/gx8002-clear-bss/clear.elf';clear_elf=Elf32(clear_path.read_bytes(),'clear');row=clear['functions'][0]
    clear_section=next(x for x in clear_elf.sections if x['name']==row['section_name']);assert sha(clear_elf.contents(clear_section))==row['compiled_sha256']
    report['runtime_state']={'section':'.probe_state','address':state['address'],'bytes':1,'type':'NOBITS','startup_clear_elf_sha256':sha(clear_path.read_bytes()),'clear_interval':[interval['bss_start'],interval['bss_end']]}
    (ROOT/'docs/research/gx8002-flash-probe-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
