#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed NPU register initialization call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_snpu_register_pointer':0x20027914,'open_cfw_gx8002_npu_set_clock_gate':0x10205618,'open_cfw_gx8002_npu_set_idle_cycle':0x10205648,'open_cfw_gx8002_npu_set_idle_mode':0x10205630,'open_cfw_gx8002_npu_clr_interrupt':0x10205768,'open_cfw_gx8002_npu_en_interrupt':0x1020566c,'open_cfw_gx8002_npu_set_overtime_thr':0x10205660}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_npu_regs_init.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'npu-regs-init-candidate.o')],check=True)
    script=out/'npu-regs-init-candidate.ld';script.write_text('SECTIONS { .text 0x10205950 : { *(.text.open_cfw_gx8002_npu_regs_init) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'npu-regs-init-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'npu-regs-init-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('NPU register initialization stock/link')
    (out/'npu-regs-init-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_npu_regs_init','section_name':'.text','package_offset':0xeedc,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':76,'stock_sha256':sha(stock[0xeedc:0xef28]),'fits':len(payload)<=76,'source_admitted':False,'limits':['Candidate only. Need live pointer reloads, exact helper ordering and arguments, and ABI checks. Only external pointer slot described; no state ownership claimed.']}
    (ROOT/'docs/research/gx8002-npu-regs-init-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
