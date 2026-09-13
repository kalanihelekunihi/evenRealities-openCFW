# SPDX-License-Identifier: MIT
"""Reproducible compiler-generated standby helpers with shared source pool."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-board';sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');deps=[]
    for rel in ('lvp/lvp_mode_tws.c','lvp/common/lvp_queue.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_tws_standby.c';assembly=out/'tws-standby-pool.s';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-mconstpool','-I'+str(sdk/'lvp/common'),'-S',str(source),'-o',str(assembly)],check=True)
    original=assembly.read_text();text=original
    for i in (0,1):
        marker=f'\t.align\t2\n.LCP{i}:\n\t.long\topen_cfw_gx8002_tws_standby_storage\n';assert text.count(marker)==1;text=text.replace(marker,'')
    text,count=re.subn(r'\t.size\topen_cfw_gx8002_tws_[^\n]+\n','',text);assert count==2
    assert text.count('\tlrw\ta3, [.LCP0]')==text.count('\tlrw\ta3, [.LCP1]')==1
    text=text.replace('\tlrw\ta3, [.LCP0]','\tlrw16\ta3, [.LCP0+2]').replace('\tlrw\ta3, [.LCP1]','\tlrw16\ta3, [.LCP0]')
    text+='\n.section .rodata.standby_pool,"a",@progbits\n.align 2\n.LCP0:\n.long open_cfw_gx8002_tws_standby_storage\n'
    state_source=ROOT/'components/shared/gx8002/runtime_gx8002_tws_standby_state.c';state_obj=out/'tws-standby-state.o'
    subprocess.run([pre+'gcc',*flags,'-c',str(state_source),'-o',str(state_obj)],check=True)
    asm=out/'tws-standby-split.s';asm.write_text(text);script=out/'tws-standby-split.ld';script.write_text('SECTIONS { .setter 0x100263b4 : { *(.text.open_cfw_gx8002_tws_set_standby) } .loop 0x100263c4 : { *(.text.open_cfw_gx8002_tws_standby_loop) } .pool 0x100264d4 : { *(.rodata.standby_pool) } .state 0x2002e738 (NOLOAD) : { *(.bss.tws_standby_words) } }\nopen_cfw_gx8002_tws_standby_storage = 0x2002e6ec;\n')
    obj=out/'tws-standby-split.o';path=out/'tws-standby-split.elf';subprocess.run([pre+'as','-mcpu=ck804ef',str(asm),'-o',str(obj)],check=True);subprocess.run([pre+'ld','-T',str(script),str(obj),str(state_obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'standby');sections=[s for s in elf.sections if s['size'] and s['flags']&2];assert len(sections)==4
    state=next(s for s in sections if s["name"]==".state");assert (state["address"],state["size"],state["type"],state["flags"])==(0x2002e738,8,8,3);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size in (('.setter',0x183c8,14),('.loop',0x183d8,24)):
        section=next(s for s in sections if s['name']==name);body=elf.contents(section);assert section['address']==offset+0x1000dfec and len(body)==size and body==stock[offset:offset+size];rows.append({'section':name,'bytes':size,'sha256':sha(body)})
    pool=next(s for s in sections if s['name']=='.pool');assert pool['address']==0x100264d4 and elf.contents(pool)==(0x2002e6ec).to_bytes(4,'little')
    assert not any(elf.relocations(s['index']) for s in sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    r={'state_source_sha256':sha(state_source.read_bytes()),'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'compiler_assembly_sha256':sha(original.encode()),'transformed_assembly_sha256':sha(text.encode()),'elf_sha256':sha(path.read_bytes()),'sections':rows,'source_admitted':False,'limits':['Guarded compiler assembly and exact stock bodies; source pool verified. State allocation and admission pending.']};(ROOT/'docs/research/gx8002-tws-standby-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(build()['sections'])
