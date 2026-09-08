#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed SNPU clock gate over source-qualified IRQ helpers."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ADDRESS=0x100251ec
OFFSET=0x17200

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='include/driver/gx_clock/gx_clock_v2.h';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();header=authenticated_blob(sdk/rel,blob)
    matches=re.findall(r'void gx_clock_set_module_snpu_enable\(int enable\);',header.decode())
    if len(matches)!=1:raise ValueError('SNPU clock public interface')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_clock.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]];probe=out/'snpu-clock-interface-probe.c';probe.write_text('#include "'+str(source)+'"\n'+matches[0]+'\n')
    subprocess.run([pre+'gcc',*flags,'-fsyntax-only',str(probe)],check=True)
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'snpu-clock-candidate.o')],check=True)
    script=out/'snpu-clock-candidate.ld';script.write_text('SECTIONS { .text 0x100251ec : { *(.text.gx_clock_set_module_snpu_enable) } }\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n')
    p=out/'snpu-clock-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'snpu-clock-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SNPU clock stock/link')
    (out/'snpu-clock-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'interface':{'path':rel,'blob':blob,'sha256':sha(header)},'flags':flags,'source_sha256':sha(source.read_bytes()),'interface_probe_sha256':sha(probe.read_bytes()),'symbol':'gx_clock_set_module_snpu_enable','section_name':'.text','package_offset':OFFSET,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':36,'stock_sha256':sha(stock[OFFSET:OFFSET+36]),'fits':len(payload)<=36,'source_admitted':False,'limits':['Candidate only. Need ordered save/MMIO/restore, exact saved-state propagation and ABI qualification. IRQ helper implementation independently source-qualified.']}
    (ROOT/'docs/research/gx8002-snpu-clock-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
