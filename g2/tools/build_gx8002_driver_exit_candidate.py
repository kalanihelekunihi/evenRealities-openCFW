#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build reconstructed driver-exit C; SDK objects supply identity evidence only."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'gx_mask_irq':0x100254fc,'gx_unmask_irq':0x10025504,'open_cfw_gx8002_snpu_suspend':0x10205a90,'open_cfw_gx8002_snpu_device_exit':0x102055ac,'open_cfw_gx8002_audio_reset':0x10203c88,'open_cfw_gx8002_platform_gate':0x10025080}
FUNCTIONS=[('gx_snpu_exit',0x10205d40,0xf2cc,32),('gx_audio_in_exit',0x10204984,0xdf10,44)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('drivers_lib/snpu/grus/snpu.o','drivers_lib/audio_in/v2.0/audio_in.o','include/driver/gx_irq.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob)),'role':'identity_oracle' if rel.endswith('.o') else 'source_interface'})
    excerpts=[]
    for name in ('gx_mask_irq','gx_unmask_irq'):
        matches=re.findall(r'void '+name+r'\(unsigned int irq\);',(sdk/'include/driver/gx_irq.h').read_text())
        if len(matches)!=1:raise ValueError('driver IRQ interface')
        excerpts.extend(matches)
    header=out/'driver-exit-interfaces.h';header.write_text('/* Exact authenticated upstream IRQ declarations. */\n'+'\n'.join(excerpts)+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_driver_exit.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-c',str(source),'-o',str(out/'driver-exit-candidate.o')],check=True)
    script=out/'driver-exit-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {a:#x} : {{ *(.text.{n}) }}\n' for n,a,o,size in FUNCTIONS)+'}\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'driver-exit-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'driver-exit-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('driver exit stock/link')
    for n,a,o,size in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('driver exit relocation')
        rows.append({'symbol':n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[o:o+size]})
    (out/'driver-exit-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'interface_header_sha256':sha(header.read_bytes()),'regions':rows,'source_admitted':False,'limits':['Reconstructed C candidate only. Need helper ordering, conditional shutdown, preserved return, ABI/frame qualification. Downstream hardware helpers remain separate.']}
    (ROOT/'docs/research/gx8002-driver-exit-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
