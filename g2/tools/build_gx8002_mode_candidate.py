#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile recovered mode init/tick against the authenticated upstream types."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS = {'lvp_idle_mode_info':0x1020b1c4, 'lvp_tws_mode_info':0x1020b204,
            'open_cfw_gx8002_mode_list':0x1020b1bc,
            'open_cfw_gx8002_mode_state':0x2002e6e4}
FUNCTIONS = [('LvpInitMode',0x102085a4,0x11b30,84), ('LvpModeTick',0x102085f8,0x11b84,36)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'; out=ROOT/'build/gx8002-board'; out.mkdir(parents=True,exist_ok=True)
    deps=[]
    for rel in ('lvp/lvp_mode.c','lvp/lvp_mode.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_mode.c'; pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'); flags=['-Os',*FLAGS[1:],'-fno-reorder-blocks']
    subprocess.run([pre+'gcc',*flags,'-I'+str(sdk/'lvp'),'-c',str(source),'-o',str(out/'mode-candidate.o')],check=True)
    script=out/'mode-candidate.ld'; script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {a:#x} : {{ *(.text.{n}) }}\n' for n,a,_,_ in FUNCTIONS)+'}\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'mode-candidate.elf'; subprocess.run([pre+'ld','-T',str(script),str(out/'mode-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p)); stock=IMAGE.read_bytes(); rows=[]
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved mode')
    for n,a,o,length in FUNCTIONS:
        s=next(x for x in e.sections if x['name']=='.text.'+n)
        if e.relocations(s['index']):raise ValueError('mode relocations')
        rows.append({'symbol':n,'section_name':s['name'],'address':a,'compiled_bytes':s['size'],'compiled_sha256':sha(e.contents(s)),
                     'package_offset':o,'stock_envelope_bytes':length,'stock_sha256':sha(stock[o:o+length]),'fits':s['size']<=length})
    (out/'mode-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'functions':rows,'source_admitted':False}
    (ROOT/'docs/research/gx8002-mode-candidate.json').write_text(json.dumps(report,indent=2)+'\n'); return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
