#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build public IRQ mask wrappers over source-qualified internal IRQ routines."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('gx_mask_irq',0x100254fc,0x17510),('gx_unmask_irq',0x10025504,0x17518)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='include/driver/gx_irq.h';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);source=ROOT/'components/shared/gx8002/runtime_gx8002_irq_mask_wrappers.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    excerpts=[]
    for name,_,_ in FUNCTIONS:
        matches=re.findall(r'void '+name+r'\(unsigned int irq\);',data.decode())
        if len(matches)!=1:raise ValueError('IRQ wrapper upstream interface')
        excerpts.extend(matches)
    probe=out/'irq-mask-interface-probe.c';probe.write_text('#include "'+str(source)+'"\n'+'\n'.join(excerpts)+'\n')
    subprocess.run([pre+'gcc',*flags,'-fsyntax-only',str(probe)],check=True)
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'irq-mask-candidate.o')],check=True)
    script=out/'irq-mask-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {a:#x} : {{ *(.text.{n}) }}\n' for n,a,o in FUNCTIONS)+'}\nopen_cfw_gx8002_irq_enable = 0x100254ac;\nopen_cfw_gx8002_irq_disable = 0x100254c8;\n')
    p=out/'irq-mask-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'irq-mask-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('IRQ mask stock/link')
    for n,a,o in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('IRQ mask relocation')
        rows.append({'symbol':n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':8,'stock_sha256':sha(stock[o:o+8]),'fits':len(payload)<=8,'exact_stock_payload':payload==stock[o:o+8]})
    (out/'irq-mask-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'interface':{'path':rel,'blob':blob,'sha256':sha(data)},'source_sha256':sha(source.read_bytes()),'interface_probe_sha256':sha(probe.read_bytes()),'flags':flags,'regions':rows,'source_admitted':False,'limits':['Candidate only. Need argument bit-pattern preservation, correct enable/disable target, helper clobber and frame qualification. Underlying IRQ operations independently source-qualified.']}
    (ROOT/'docs/research/gx8002-irq-mask-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
