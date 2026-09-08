#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build MAX initialization and diagnostic from typed source, not stock bytes."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/vui/kws/max_decoder.c','include/lvp_param.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    header=out/'max-init-upstream-types.h';parts=[]
    for name in ('LVP_KWS_PARAM','LVP_KWS_PARAM_LIST'):
        found=re.findall(r'typedef struct \{[^}]*\} '+name+';', (sdk/'include/lvp_param.h').read_text())
        if len(found)!=1:raise ValueError('MAX parameter type')
        parts.append(found[0])
    header.write_text('/* Exact authenticated upstream parameter types. */\n'+'\n'.join(parts)+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_max_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-c',str(source),'-o',str(out/'max-initialize-candidate.o')],check=True)
    script=out/'max-initialize-candidate.ld';script.write_text('SECTIONS { .text 0x10208944 : { *(.text.LvpInitMaxKws) } .rodata.message 0x1020b30d : { *(.rodata.open_cfw_gx8002_max_init_error) } }\nopen_cfw_gx8002_max_keyword_list = 0x2002e79c;\nprintf = 0x10206c24;\nKwsStrategyInit = 0x10208978;\n')
    p=out/'max-initialize-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'max-initialize-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('MAX stock/link invariant')
    for name,o,size in (('.text',0x11ed0,32),('.rodata.message',0x14899,66)):
        sec=next(s for s in e.sections if s['name']==name);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('MAX relocation')
        rows.append({'section_name':name,'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[o:o+size]})
    (out/'max-initialize-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'type_header_sha256':sha(header.read_bytes()),'regions':rows,'source_admitted':False,'limits':['Candidate only. Need count branches, helper call ordering and stack qualification; list state and complete MAX decoding remain separate.']}
    (ROOT/'docs/research/gx8002-max-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
