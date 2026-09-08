#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed SNPU ISR call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_snpu_isr_state':0x20027350,'open_cfw_gx8002_snpu_process_status':0x10205bd8}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_isr.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap']
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'snpu-isr-candidate.o')],check=True)
    script=out/'snpu-isr-candidate.ld';script.write_text('SECTIONS { .text 0x10205ce0 : { *(.text.open_cfw_gx8002_snpu_isr) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'snpu-isr-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'snpu-isr-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SNPU ISR stock/link')
    (out/'snpu-isr-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_snpu_isr','section_name':'.text','package_offset':0xf26c,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':20,'stock_sha256':sha(stock[0xf26c:0xf280]),'fits':len(payload)<=20,'source_admitted':False,'limits':['Candidate only. Need state comparison, conditional helper call, observed return and ABI qualification. Private original return types remain inferred; source explicitly preserves r0. process_status remains unrecovered.']}
    (ROOT/'docs/research/gx8002-snpu-isr-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
