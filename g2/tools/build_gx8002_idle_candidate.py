#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile IDLE callbacks, messages and typed mode object from source on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
DELTA=0x101f6a74
CODE=[('open_cfw_gx8002_idle_tick',0x1020861c,4),('open_cfw_gx8002_idle_buffer_init',0x10208620,4),
      ('open_cfw_gx8002_idle_done',0x10208624,16),('open_cfw_gx8002_idle_init',0x10208634,16)]
DATA=[('lvp_idle_mode_info',0x1020b1c4,20),('open_cfw_gx8002_idle_exit_message',0x1020b1d8,22),
      ('open_cfw_gx8002_idle_init_message',0x1020b1ee,22)]
PRINTF=0x10206c24
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/lvp_mode_idle.c','lvp/lvp_mode.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_mode_idle.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(sdk/'lvp'),'-c',str(source),'-o',str(out/'idle-candidate.o')],check=True)
    sections=[('.text.'+n,n,a,size,'compiled_c') for n,a,size in CODE]+[('.rodata.'+n,n,a,size,'generated_source_data') for n,a,size in DATA]
    script=out/'idle-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'{s} {a:#x} : {{ *({s}) }}\n' for s,n,a,size,k in sections)+'}\n'+f'printf = {PRINTF:#x};\n')
    p=out/'idle-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'idle-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved idle')
    for name,symbol,address,size,kind in sections:
        sec=next(x for x in e.sections if x['name']==name);payload=e.contents(sec);offset=address-DELTA
        if e.relocations(sec['index']):raise ValueError('idle relocations')
        if kind=='generated_source_data' and payload!=stock[offset:offset+size]:raise ValueError('idle source data mismatch')
        rows.append({'symbol':symbol,'section_name':name,'address':address,'ownership_kind':kind,
                     'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                     'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size})
    (out/'idle-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'functions':rows,'source_admitted':False}
    (ROOT/'docs/research/gx8002-idle-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
