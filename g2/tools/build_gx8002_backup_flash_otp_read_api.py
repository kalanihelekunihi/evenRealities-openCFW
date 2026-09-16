#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed flash read API callback wrapper; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-flash-otp-read-api';out.mkdir(parents=True,exist_ok=True);rel='boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_flash.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'flash-otp-read-api-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_read_api.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'flash-otp-read-api-candidate.o')],check=True)
    script=out/'flash-otp-read-api-candidate.ld';script.write_text('SECTIONS { .text 0x1000802c : { *(.text.open_cfw_gx8002_flash_otp_read_api) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'flash-otp-read-api-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'flash-otp-read-api-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('backup OTP read API stock/link')
    if len(payload)>28 or any(s['flags']&2 and s['size'] and s['name']!='.text' for s in e.sections):raise ValueError('OTP read API placement overflow or unexpected allocation')
    (out/'flash-otp-read-api-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'board_call_site_reference_only; implementation recovered from stock'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'interface_layout_sha256':sha((source.parent/'runtime_gx8002_flash_interface_table.h').read_bytes()),'symbol':'open_cfw_gx8002_flash_otp_read_api','section_name':'.text','package_offset':0x4096c,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':28,'stock_sha256':sha(stock[0x4096c:0x40988]),'fits':len(payload)<=28,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    (ROOT/'docs/research/gx8002-backup-flash-otp-read-api-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
