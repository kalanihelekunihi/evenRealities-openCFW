# SPDX-License-Identifier: MIT
"""Compile recovered backup system initialization without binary pull-through."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ROWS=(('initialize',0x4322c,480),)

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/lvp_system_init.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    upstream={'path':rel,'blob':blob,'sha256':sha(subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob]))}
    out=ROOT/'build/gx8002-backup-lvp-system-initialize';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_lvp_system_initialize.c';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'buffers.o')],check=True)
    data_source=source.with_name('runtime_gx8002_backup_lvp_system_data.c')
    subprocess.run([pre+'gcc',*flags,'-c',str(data_source),'-o',str(out/'data.o')],check=True)
    symbols=json.loads((ROOT/'docs/research/gx8002-backup-lvp-system-symbol-map.json').read_text())
    sections=['SECTIONS {']
    for name,address in symbols.items():
        if name.startswith('sys_'):sections.append('.rodata.'+name+' '+hex(address)+' : { *(.rodata.'+name+') }')
    for suffix,offset,size in ROWS:
        sections.append('.text.'+suffix+' '+hex(offset+(0x10000000-0x38940))+' : { *(.text.open_cfw_gx8002_backup_lvp_system_'+suffix+') }')
    sections.append('}')
    sections.extend(name+' = '+hex(address)+';' for name,address in symbols.items() if not name.startswith('sys_'))
    (out/'buffers.ld').write_text('\n'.join(sections)+'\n')
    subprocess.run([pre+'ld','-T',str(out/'buffers.ld'),str(out/'buffers.o'),str(out/'data.o'),'-o',str(out/'buffers.elf')],check=True)
    elf=Elf32((out/'buffers.elf').read_bytes(),'buffers')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name'] not in ('.text.initialize',) and not s['name'].startswith('.rodata.sys_') for s in elf.sections):raise ValueError('Unowned allocation')
    (out/'buffers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'buffers.elf')],text=True))
    functions=[]
    for suffix,offset,size in ROWS:
        payload=elf.contents(next(s for s in elf.sections if s['name']=='.text.'+suffix))
        functions.append({'symbol':'open_cfw_gx8002_backup_lvp_system_'+suffix,'section_name':'.text.'+suffix,'package_offset':offset,'stock_envelope_bytes':size,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size,'exact_stock':payload==stock[offset:offset+size]})
    for name,address in symbols.items():
        if not name.startswith('sys_'):continue
        section='.rodata.'+name;payload=elf.contents(next(s for s in elf.sections if s['name']==section));offset=address-(0x10000000-0x38940);size=len(payload)
        if payload!=stock[offset:offset+size]:raise ValueError(('Data mismatch',name,payload,stock[offset:offset+size]))
        functions.append({'symbol':name,'section_name':section,'package_offset':offset,'stock_envelope_bytes':size,'compiled_bytes':size,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[offset:offset+size]),'fits':True,'exact_stock':True,'ownership_kind':'generated_source_data'})
    return {'data_source_sha256':sha(data_source.read_bytes()),'functions':functions,'source_sha256':sha(source.read_bytes()),'flags':flags,'upstream':upstream,'source_admitted':False,'limits':['Candidate only; see separate backup initializer execution verification. Helpers and hardware require separate qualification.']}
if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-backup-lvp-system-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['compiled_bytes'],r['stock_envelope_bytes']) for r in report['functions']])
