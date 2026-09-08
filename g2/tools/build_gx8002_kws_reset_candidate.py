#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile keyword strategy reset/init and their source-defined BSS object."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('KwsStrategyReset',0x10208964,0x11ef0,20),('KwsStrategyInit',0x10208978,0x11f04,8)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/vui/kws/kws_strategy.c','lvp/vui/kws/kws_strategy.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    matches=re.findall(r'typedef struct \{[^}]*\} LVP_ACTIVATION_KWS;', (sdk/'lvp/vui/kws/kws_strategy.h').read_text())
    if len(matches)!=1:raise ValueError('activation type changed')
    header=out/'kws-reset-upstream-types.h';header.write_text('/* Exact authenticated upstream activation type. */\n'+matches[0]+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_reset.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-c',str(source),'-o',str(out/'kws-reset-candidate.o')],check=True)
    script=out/'kws-reset-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {a:#x} : {{ *(.text.{n}) }}\n' for n,a,o,size in FUNCTIONS)+'.bss.activation 0x2002e7a8 (NOLOAD) : { *(.bss.open_cfw_gx8002_activation_list) }\n}\nmemset = 0x102099cc;\n')
    p=out/'kws-reset-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'kws-reset-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('reset stock/link invariant')
    for n,a,o,size in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('reset relocation')
        rows.append({'symbol':n,'section_name':sec['name'],'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':o,'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[o:o+size]})
    bss=next(s for s in e.sections if s['name']=='.bss.activation')
    if bss['address']!=0x2002e7a8 or bss['size']!=164 or bss['type']!=8:raise ValueError('activation BSS definition')
    (out/'kws-reset-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'type_header_sha256':sha(header.read_bytes()),'functions':rows,'source_bss':{'address':bss['address'],'size':bss['size'],'section_type':'SHT_NOBITS'},'source_admitted':False,'limits':['Candidate reset/init plus BSS definition only. Need decoded calls, frame and memset extent qualification; no source ownership registered yet.']}
    (ROOT/'docs/research/gx8002-kws-reset-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
