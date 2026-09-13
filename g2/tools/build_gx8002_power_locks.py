# SPDX-License-Identifier: MIT
"""Compile recovered power lock allocation and query without binary pull-through."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ROWS=(('lock_create',0x10cfc,56),('is_locked',0x10d84,16))

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/lvp_pmu.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    upstream={'path':rel,'blob':blob,'sha256':sha(subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob]))}
    out=ROOT/'build/gx8002-power-locks';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_power_locks.c';flags=['-Os',*FLAGS[1:],'-fno-peel-loops','-fno-tree-ch']
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'buffers.o')],check=True)
    sections=['SECTIONS {']
    for suffix,offset,size in ROWS:
        sections.append('.text.'+suffix+' '+hex(offset+0x101f6a74)+' : { *(.text.open_cfw_gx8002_power_'+suffix+') }')
    sections.append('}')
    sections.append('gx_pmu_get_wakeup_source = 0x10024940; memset = 0x102099cc; open_cfw_gx8002_power_state = 0x2002dfbc;')
    (out/'buffers.ld').write_text('\n'.join(sections)+'\n')
    subprocess.run([pre+'ld','-T',str(out/'buffers.ld'),str(out/'buffers.o'),'-o',str(out/'buffers.elf')],check=True)
    elf=Elf32((out/'buffers.elf').read_bytes(),'buffers')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name'] not in tuple('.text.'+row[0] for row in ROWS) for s in elf.sections):raise ValueError('Unowned allocation')
    (out/'buffers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'buffers.elf')],text=True))
    functions=[]
    for suffix,offset,size in ROWS:
        payload=elf.contents(next(s for s in elf.sections if s['name']=='.text.'+suffix))
        functions.append({'symbol':'open_cfw_gx8002_power_'+suffix,'section_name':'.text.'+suffix,'package_offset':offset,'stock_envelope_bytes':size,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size,'exact_stock':payload==stock[offset:offset+size]})
    return {'functions':functions,'source_sha256':sha(source.read_bytes()),'flags':flags,'upstream':upstream,'source_admitted':False,'limits':['Candidate only; decoded initialization and callback qualification pending.']}
if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-power-locks-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['compiled_bytes'],r['stock_envelope_bytes']) for r in report['functions']])
