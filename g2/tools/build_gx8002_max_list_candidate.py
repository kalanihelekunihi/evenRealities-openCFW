#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build source MAX parameter registration/listing, BSS state and messages."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
MESSAGES=[('header',0x1020b2ae,43),('word',0x1020b2d9,27),('value',0x1020b2f4,12),('threshold',0x1020b300,13),('newline',0x1020b7c2,2)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/vui/kws/max_decoder.c','include/lvp_param.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    header=out/'max-list-upstream-types.h';parts=[]
    for name in ('LVP_KWS_PARAM','LVP_KWS_PARAM_LIST'):
        found=re.findall(r'typedef struct \{[^}]*\} '+name+';', (sdk/'include/lvp_param.h').read_text())
        if len(found)!=1:raise ValueError('MAX list type')
        parts.append(found[0])
    header.write_text('/* Exact authenticated upstream parameter types. */\n'+'\n'.join(parts)+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_max_list.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-c',str(source),'-o',str(out/'max-list-candidate.o')],check=True)
    script=out/'max-list-candidate.ld';script.write_text('SECTIONS { .text 0x10208880 : { *(.text.LvpPrintMaxKwsList) }\n'+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_max_list_{n}) }}\n' for n,a,size in MESSAGES)+'.bss.list 0x2002e79c (NOLOAD) : { *(.bss.open_cfw_gx8002_max_keyword_list) }\n}\nopen_cfw_gx8002_wakeword_parameters = 0x20026c7c;\nprintf = 0x10206c24;\n')
    p=out/'max-list-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'max-list-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('MAX list stock/link invariant')
    for name,o,size in [('.text',0x11e0c,120)]+[('.rodata.'+n,a-0x101f6a74,size) for n,a,size in MESSAGES]:
        sec=next(s for s in e.sections if s['name']==name);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('MAX list relocation')
        rows.append({'section_name':name,'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[o:o+size]})
    bss=next(s for s in e.sections if s['name']=='.bss.list')
    if bss['size']!=8 or bss['address']!=0x2002e79c or bss['type']!=8:raise ValueError('MAX list BSS')
    (out/'max-list-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'type_header_sha256':sha(header.read_bytes()),'regions':rows,'defined_bss':{'address':bss['address'],'size':8},'source_admitted':False,'limits':['Candidate only. Need live count/pointer reload, printf argument, state write and frame qualification. Parameter table has separate source ownership; no full MAX decoder/hardware claim.']}
    (ROOT/'docs/research/gx8002-max-list-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
