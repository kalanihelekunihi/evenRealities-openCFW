# SPDX-License-Identifier: MIT
"""Compile typed mode descriptor and callback references on macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
ROWS=(('mode_list',0x14748,8),('tws_info',0x14790,20))
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('lvp/lvp_mode.h','lvp/lvp_mode.c','lvp/lvp_mode_tws.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-mode-descriptors';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_mode_descriptors.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-Wall','-Wextra','-Werror','-I'+str(sdk/'lvp'),'-c',str(source),'-o',str(out/'descriptors.o')],check=True)
    bindings={'lvp_idle_mode_info':0x1020b1c4,'open_cfw_gx8002_tws_init':0x10208670,'open_cfw_gx8002_tws_done':0x1020864c,'open_cfw_gx8002_tws_tick':0x10026358,'open_cfw_gx8002_tws_buffer_init':0x10208644}
    (out/'descriptors.ld').write_text('SECTIONS {\n'+''.join(f'.{name} {offset+0x101f6a74:#x} : {{ *(.rodata.{name}) }}\n' for name,offset,size in ROWS)+'}\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()));path=out/'descriptors.elf';subprocess.run([pre+'ld','-T',str(out/'descriptors.ld'),str(out/'descriptors.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'descriptors');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==2
    for name,offset,size in ROWS:
        s=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(s);assert s['address']==offset+0x101f6a74 and s['flags']==2 and len(body)==size and body==stock[offset:offset+size] and not elf.relocations(s['index'])
        rows.append({'name':name,'package_offset':offset,'bytes':size,'sha256':sha(body)})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    return {'sdk_commit':SDK_COMMIT,'upstream':upstream,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'bindings':bindings,'rows':rows,'source_admitted':False,'limits':['Typed SDK mode info/list with named callback references compiles byte-exact. No raw pointer arrays or duplicate idle state.','Registered callback ownership and composed dispatch still need verification before admission.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-mode-descriptors-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Typed mode descriptor bytes:',sum(x['bytes'] for x in r['rows']))
