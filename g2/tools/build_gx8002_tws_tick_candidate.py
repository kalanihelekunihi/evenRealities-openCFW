# SPDX-License-Identifier: MIT
"""Rebuild TWS tick C with guarded short shared-pool loads."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');deps=[]
    for rel in ('lvp/lvp_mode_tws.c','lvp/common/lvp_queue.h','include/lvp_context.h','include/lvp_attr.h','lvp/app_core/lvp_app_core.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    config=out/'tws-tick-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_tws_tick.c';assembly=out/'tws-tick-pool.s';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-mconstpool','-I'+str(config),'-I'+str(sdk/'include'),'-I'+str(sdk/'lvp/common'),'-I'+str(sdk/'lvp/app_core'),'-S',str(source),'-o',str(assembly)],check=True)
    original=assembly.read_text();pool='\t.align\t2\n.LCP0:\n\t.long\topen_cfw_gx8002_tws_tick_state\n';size='\t.size\topen_cfw_gx8002_tws_tick, .-open_cfw_gx8002_tws_tick'
    assert original.count(pool)==original.count(size)==1
    assert original.count('\tlrw\ta0, [.LCP0]')==original.count('\tlrw\ta3, [.LCP0]')==1
    transformed=original.replace('\tlrw\ta0, [.LCP0]','\tlrw16\ta0, [.LCP0+2]').replace('\tlrw\ta3, [.LCP0]','\tlrw16\ta3, [.LCP0]').replace(pool,'\t.section .rodata.tws_tick_pool,"a",@progbits\n'+pool).replace(size,'')
    asm=out/'tws-tick-split.s';asm.write_text(transformed)
    bindings={n:a+0x1000dfec for n,a in {'LvpQueueGet':0x1f8fc4,'LvpDoMaxDecoder':0x1fa90c,'LvpAudioInUpdateReadIndex':0x1f93b4,'LvpTriggerAppEvent':0x1facd4,'LvpPmuSuspendIsLocked':0x1f980c,'LvpPmuSuspend':0x1f981c}.items()};bindings['open_cfw_gx8002_tws_tick_state']=0x2002e6ec
    script=out/'tws-tick-split.ld';script.write_text('SECTIONS { .text 0x10026358 : { *(.text*) } .pool 0x100264d4 : { *(.rodata.tws_tick_pool) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    obj=out/'tws-tick-split.o';path=out/'tws-tick-split.elf';subprocess.run([pre+'as','-mcpu=ck804ef',str(asm),'-o',str(obj)],check=True);subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'tick');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==2
    text=next(s for s in sections if s['name']=='.text');literal=next(s for s in sections if s['name']=='.pool');body=elf.contents(text);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert (text['address'],text['size'])==(0x10026358,90) and body==stock[0x1836c:0x183c6]
    assert literal['address']==0x100264d4 and elf.contents(literal)==(0x2002e6ec).to_bytes(4,'little')
    assert not any(elf.relocations(s['index']) for s in sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    r={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'compiler_assembly_sha256':sha(original.encode()),'transformed_assembly_sha256':sha(transformed.encode()),'elf_sha256':sha(path.read_bytes()),'body_sha256':sha(body),'body_bytes':90,'bindings':bindings,'source_admitted':False,'limits':['Exact stock instruction match guards halfword-PC cross-section relocation addend. Source pool literal verified separately. Full behavior, PMU prototypes and combined shared-pool admission pending.']}
    (ROOT/'docs/research/gx8002-tws-tick-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(build()['body_bytes'])
