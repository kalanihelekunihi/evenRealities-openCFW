#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed NPU enable/disable/status wrappers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('enable',0xeb80),('disable',0xeb8c),('is_enabled',0xeb98),('all_idle',0xec70)]
DELTA=0x101f6a74

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu_regs.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob);source=ROOT/'components/shared/gx8002/runtime_gx8002_npu_control.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'npu-control-candidate.o')],check=True)
    script=out/'npu-control-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {o+DELTA:#x} : {{ *(.text.open_cfw_gx8002_npu_{n}) }}\n' for n,o in FUNCTIONS)+'}\nopen_cfw_gx8002_reg_get_bit = 0x102055c0;\nopen_cfw_gx8002_reg_set_bit = 0x102055cc;\nopen_cfw_gx8002_reg_clear_bit = 0x102055dc;\n')
    p=out/'npu-control-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'npu-control-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('NPU control stock/link')
    for n,o in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('NPU control relocation')
        rows.append({'symbol':'open_cfw_gx8002_npu_'+n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':12,'stock_sha256':sha(stock[o:o+12]),'fits':len(payload)<=12})
    (out/'npu-control-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle)},'source_sha256':sha(source.read_bytes()),'flags':flags,'regions':rows,'source_admitted':False,'limits':['Candidate only. Need register-helper target/argument/return/frame qualification. Primitive helpers separately qualified.']}
    (ROOT/'docs/research/gx8002-npu-control-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
