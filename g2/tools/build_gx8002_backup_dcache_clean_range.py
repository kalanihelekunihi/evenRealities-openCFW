#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed cache-clean range call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-dcache-clean-range';out.mkdir(exist_ok=True);rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_dcache.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_dcache_clean_range.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'dcache-clean-range-candidate.o')],check=True)
    script=out/'dcache-clean-range-candidate.ld';script.write_text('SECTIONS { .text 0x10004e74 : { *(.text.open_cfw_gx8002_dcache_clean_range) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'dcache-clean-range-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'dcache-clean-range-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('cache-clean range stock/link')
    (out/'dcache-clean-range-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'unrelated_snpu_object_identity_only'},'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_dcache_clean_range','section_name':'.text','package_offset':0x3d7b4,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':156,'stock_sha256':sha(stock[0x3d7b4:0x3d850]),'fits':len(payload)<=156,'source_admitted':False,'limits':['Candidate only. Need signed-size boundaries, all ordered cache command writes, address wrapping, large-size prefixes and ABI checks. No hardware cache coherence qualification.']}
    (ROOT/'docs/research/gx8002-backup-dcache-clean-range-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
