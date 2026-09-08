#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproduce application startup placement using authenticated SDK types."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';output=ROOT/'build/gx8002-app-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';source=ROOT/'components/shared/gx8002/runtime_gx8002_app_initialize.c'
    dependencies=[]
    for name in ('lvp/app_core/lvp_app.h','lvp/app_core/lvp_app_core.h','lvp/common/lvp_queue.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        dependencies.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    flags=FLAGS+['-fno-shrink-wrap'];obj=output/'app-initialize.o'
    subprocess.run([str(prefix)+'gcc',*flags,'-I',str(sdk/'lvp/app_core'),'-I',str(sdk/'lvp/common'),'-I',str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
    script=output/'app-initialize.ld';script.write_text('''SECTIONS {
.text.open_cfw_gx8002_app_initialize 0x10208cd4 : { *(.text.open_cfw_gx8002_app_initialize) }
.rodata.suspend_name 0x1020b3ee : SUBALIGN(1) { *(.rodata.suspend_name) }
.rodata.resume_name 0x1020b3fd : SUBALIGN(1) { *(.rodata.resume_name) }
}
LvpQueueInit = 0x10206f9c;
open_cfw_gx8002_app_core_ops = 0x20026d38;
open_cfw_gx8002_app_event_queue = 0x2002ecd8;
open_cfw_gx8002_app_event_buffer = 0x2002e880;
open_cfw_gx8002_app_suspend = 0x10208ca0;
open_cfw_gx8002_app_resume = 0x10208c7c;
open_cfw_gx8002_register_suspend = 0x102076c0;
open_cfw_gx8002_register_resume = 0x10207718;
open_cfw_gx8002_watchdog_initialize = 0x10206720;
open_cfw_gx8002_watchdog_callback = 0x10208c98;
''')
    linked=output/'app-initialize.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved startup dependency')
    for name,address,size in [('.text.open_cfw_gx8002_app_initialize',0x10208cd4,116),('.rodata.suspend_name',0x1020b3ee,15),('.rodata.resume_name',0x1020b3fd,14)]:
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section);offset=address-0x101f6a74
        if len(payload)>size or section['address']!=address or elf.relocations(section['index']):raise ValueError('startup placement failure')
        if payload!=stock[offset:offset+size]:raise ValueError('startup section differs from stock')
        rows.append({'section':name,'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    report={'source_sha256':sha(source.read_bytes()),'local_header_sha256':sha((source.parent/'runtime_gx8002_power_registration.h').read_bytes()),'sdk_commit':SDK_COMMIT,'dependencies':dependencies,'flags':flags,'sections':rows,'source_admitted':False,'limits':['Startup callback/call-order comparison pending.','State remains retained; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-app-initialize-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
