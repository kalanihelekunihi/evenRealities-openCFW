#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed SNPU internal resume call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_snpu_resume_state':0x20027350,'open_cfw_gx8002_npu_is_enabled':0x1020560c,'open_cfw_gx8002_npu_disable':0x10205600,'open_cfw_gx8002_npu_all_idle':0x102056e4,'gx_clock_set_module_snpu_enable':0x100251ec,'open_cfw_gx8002_npu_reset':0x10205880,'open_cfw_gx8002_npu_regs_init':0x10205950}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_resume_internal.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'snpu-resume-internal-candidate.o')],check=True)
    script=out/'snpu-resume-internal-candidate.ld';script.write_text('SECTIONS { .text 0x1020599c : { *(.text.open_cfw_gx8002_snpu_resume_internal) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'snpu-resume-internal-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'snpu-resume-internal-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SNPU internal resume stock/link')
    (out/'snpu-resume-internal-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_snpu_resume_internal','section_name':'.text','package_offset':0xef28,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':76,'stock_sha256':sha(stock[0xef28:0xef74]),'fits':len(payload)<=76,'source_admitted':False,'limits':['Candidate only. Need live pointer reloads, state reads/writes, helper ordering, wait completion/noncompletion and ABI checks. State layout has explicit unmodeled fields; no state ownership claimed.']}
    (ROOT/'docs/research/gx8002-snpu-resume-internal-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
