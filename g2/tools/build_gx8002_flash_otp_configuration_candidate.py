#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build recovered OTP configuration decision; placement not yet qualified."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_clock_frequency':0x10025210,'open_cfw_gx8002_flash_otp_probe':0x20026504,'open_cfw_gx8002_flash_otp_read_api':0x100247f4,'printf':0x10206c24,'strncmp':0x10206c7c,'open_cfw_gx8002_flash_otp_error':0x100249f4,'open_cfw_gx8002_flash_otp_signature':0x10024a0a}

def build(extra_flags=()):
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_clock/gx_clock_v2.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'flash-otp-configuration-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_configuration.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap',*extra_flags]
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'flash-otp-configuration-candidate.o')],check=True)
    strings=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_strings.c'
    subprocess.run([pre+'gcc',*flags,'-c',str(strings),'-o',str(out/'flash-otp-strings.o')],check=True)
    string_sections={'.rodata.otp_error':(0x16a08,22),'.rodata.otp_signature':(0x16a1e,6)}
    script=out/'flash-otp-configuration-candidate.ld';script.write_text('SECTIONS { .text 0x10025d04 : { *(.text.open_cfw_gx8002_flash_otp_configuration) } '+''.join(f'{name} {offset+0x1000dfec:#x} : {{ *({name}) }} ' for name,(offset,size) in string_sections.items())+'}\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items() if k not in ('open_cfw_gx8002_flash_otp_error','open_cfw_gx8002_flash_otp_signature')))
    p=out/'flash-otp-configuration-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'flash-otp-configuration-candidate.o'),str(out/'flash-otp-strings.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if stock[0x16a1e:0x16a24]!=b'8003A\0':raise ValueError('OTP signature length changed')
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('OTP configuration stock/link')
    string_rows=[]
    for name,(offset,size) in string_sections.items():
        section=next(s for s in e.sections if s['name']==name);data=e.contents(section)
        if section['address']!=offset+0x1000dfec or data!=stock[offset:offset+size] or e.relocations(section['index']):raise ValueError('OTP source string placement/content')
        string_rows.append({'section_name':name,'package_offset':offset,'bytes':size,'sha256':sha(data)})
    if {s['name'] for s in e.sections if s['flags']&2 and s['size']}!={'.text',*string_sections}:raise ValueError('Unexpected OTP allocation')
    if any(s['value']!=value for s in e.symbols() if s['name'] in BINDINGS for value in [BINDINGS[s['name']]]):raise ValueError('OTP symbol address')
    (out/'flash-otp-configuration-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'strings':string_rows,'strings_source_sha256':sha(strings.read_bytes()),'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'board_call_site_reference_only; implementation recovered from stock'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_flash_otp_configuration','section_name':'.text','package_offset':0x17d18,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':112,'stock_sha256':sha(stock[0x17d18:0x17d88]),'fits':len(payload)<=112,'source_admitted':False,'limits':['Build-only candidate. Source strings linked and byte-checked. Probe ABI, contained literal use, nested OTP and caller behavior require qualification before admission.']}
    (ROOT/'docs/research/gx8002-flash-otp-configuration-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
