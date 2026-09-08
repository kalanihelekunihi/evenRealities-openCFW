#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed SNPU status processing call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_snpu_process_words':0x20027350,'open_cfw_gx8002_npu_get_interrupt':0x102056f0,'open_cfw_gx8002_npu_clr_interrupt_without_overflow':0x102057e0,'open_cfw_gx8002_npu_get_over_cmd_addr':0x10205860,'open_cfw_gx8002_npu_get_op_overflow_cmd_addr':0x10205870,'open_cfw_gx8002_npu_clr_overflow_interrupt':0x10205838,'open_cfw_gx8002_snpu_suspend':0x10205a90,'open_cfw_gx8002_snpu_overtime_reset':0x10205b1c}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_snpu.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    config=out/'snpu-process-status-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_process_status.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-move-loop-invariants']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'snpu-process-status-candidate.o')],check=True)
    script=out/'snpu-process-status-candidate.ld';script.write_text('SECTIONS { .text 0x10205bd8 : { *(.text.open_cfw_gx8002_snpu_process_status) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'snpu-process-status-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'snpu-process-status-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SNPU status processing stock/link')
    (out/'snpu-process-status-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_snpu_process_status','section_name':'.text','package_offset':0xf164,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':264,'stock_sha256':sha(stock[0xf164:0xf26c]),'fits':len(payload)<=264,'source_admitted':False,'limits':['Candidate only. Need full event priority, ring traversal, callback/state mutations, wrap behavior, never-completing prefixes, state accesses and ABI qualification. Candidate only; state and descriptor semantics remain partially unmodeled.']}
    (ROOT/'docs/research/gx8002-snpu-process-status-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
