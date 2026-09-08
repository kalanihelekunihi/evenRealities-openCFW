#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build source-derived keyword activation insertion on native macOS C-SKY."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'printf':0x10206c24,'open_cfw_gx8002_activation_list':0x2002e7a8,'open_cfw_gx8002_kws_overflow_message':0x1020b34f}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/vui/kws/kws_strategy.c','lvp/vui/kws/kws_strategy.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    matches=re.findall(r'typedef struct \{[^}]*\} LVP_ACTIVATION_KWS;', (sdk/'lvp/vui/kws/kws_strategy.h').read_text())
    if len(matches)!=1:raise ValueError('activation type changed')
    header=out/'kws-upstream-types.h';header.write_text('/* Exact authenticated upstream activation type. */\n'+matches[0]+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_insert.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap','-fira-algorithm=priority']
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-c',str(source),'-o',str(out/'kws-insert-candidate.o')],check=True)
    script=out/'kws-insert-candidate.ld';script.write_text('SECTIONS { .text 0x10208980 : { *(.text.KwsStragegyInsertKwsActivation) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'kws-insert-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'kws-insert-candidate.o'),'-o',str(p)],check=True)
    elf=Elf32(p.read_bytes(),str(p));sec=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('KWS stock/link invariant')
    payload=elf.contents(sec);(out/'kws-insert-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'type_header_sha256':sha(header.read_bytes()),'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0x11f0c,'stock_envelope_bytes':144,'stock_sha256':sha(stock[0x11f0c:0x11f9c]),'fits':len(payload)<=144,'exact_stock_payload':payload==stock[0x11f0c:0x11f9c],'source_admitted':False,'limits':['Candidate only; floating-point comparisons, list accesses, invalid count domain, call ABI and insertion/update behavior need qualification.']}
    (ROOT/'docs/research/gx8002-kws-insert-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
