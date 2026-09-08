#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed SNPU initialization call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_snpu_initialize_state':0x20027350,'open_cfw_gx8002_snpu_device_init':0x102055a8,'open_cfw_gx8002_snpu_tcb_init':0x102058d4,'open_cfw_gx8002_snpu_request_irq':0x102055b0,'open_cfw_gx8002_snpu_isr':0x10205ce0}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'snpu-initialize-candidate.o')],check=True)
    script=out/'snpu-initialize-candidate.ld';script.write_text('SECTIONS { .text 0x10205cf4 : { *(.text.open_cfw_gx8002_snpu_initialize) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'snpu-initialize-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'snpu-initialize-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SNPU initialization stock/link')
    (out/'snpu-initialize-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_snpu_initialize','section_name':'.text','package_offset':0xf280,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':76,'stock_sha256':sha(stock[0xf280:0xf2cc]),'fits':len(payload)<=76,'source_admitted':False,'limits':['Candidate only. Need ordered state writes, helper/ISR arguments, helper mutations, return value and ABI qualification. TCB initialization and ISR remain separately unrecovered. No state ownership claimed.']}
    (ROOT/'docs/research/gx8002-snpu-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
