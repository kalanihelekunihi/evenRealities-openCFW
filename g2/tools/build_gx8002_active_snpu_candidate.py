# SPDX-License-Identifier: MIT
"""Reproducible standalone source build; shared pool placement remains pending."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha,IMAGE,IMAGE_SHA
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/lvp_mode_tws.c','lvp/common/lvp_queue.h','include/driver/gx_snpu.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    config=out/'active-snpu-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_active_snpu_callback.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]];obj=out/'active-snpu-callback.o'
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-I'+str(sdk/'lvp/common'),'-c',str(source),'-o',str(obj)],check=True)
    bindings={'LvpQueuePut':0x100261b8,'open_cfw_gx8002_active_snpu_queue':0x2002e6ec}
    script=out/'active-snpu.ld';script.write_text('SECTIONS { .text 0x10026340 : { *(.text.open_cfw_gx8002_active_snpu_callback) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    path=out/'active-snpu.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'active callback');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1
    section=sections[0];assert section['address']==0x10026340 and not elf.relocations(section['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'active-snpu.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sha(source.read_bytes()),'flags':flags,'bindings':bindings,'elf_sha256':sha(path.read_bytes()),'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_offset':0x18354,'stock_bytes':24,'stock_sha256':sha(stock[0x18354:0x1836c]),'fits':section['size']<=24,'source_admitted':False,'limits':['Standalone link exceeds original envelope; not suitable for replacement. Stock pool shared at package 0x184e8. Behavior and queue ownership pending.']}
    (ROOT/'docs/research/gx8002-active-snpu-candidate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['compiled_bytes'])
