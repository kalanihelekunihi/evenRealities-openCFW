# SPDX-License-Identifier: MIT
"""Build recovered TWS audio callback and source diagnostic on macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-board';sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');deps=[]
    for rel in ('lvp/lvp_mode_tws.c','include/lvp_context.h','include/lvp_attr.h','include/lvp_buffer.h','lvp/common/lvp_queue.h','lvp/app_core/lvp_app_core.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    config=out/'tws-audio-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n');flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap'];sources={};objects=[]
    for name in ('callback','state'):
        source=ROOT/f'components/shared/gx8002/runtime_gx8002_tws_audio_{name}.c';obj=out/f'tws-audio-{name}.o';sources[source.name]=sha(source.read_bytes());objects.append(obj)
        subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-I'+str(sdk/'lvp/common'),'-I'+str(sdk/'lvp/app_core'),'-c',str(source),'-o',str(obj)],check=True)
    bindings={n:a+0x1000dfec for n,a in {'LvpGetContext':0x1f8edc,'LvpGetMicFrame':0x1f8f1c,'LvpAudioInGetDelayedFFTVad':0x1f93a8,'LvpAuidoInQueryEnvNoise':0x1f95dc,'LvpGetContextHeader':0x1f8eb0,'open_cfw_gx8002_tws_standby_loop':0x183d8,'LvpKwsRun':0x180f8,'printf':0x1f8c38,'LvpTriggerAppEvent':0x1facd4}.items()};bindings['open_cfw_gx8002_tws_audio_state']=0x2002e6ec;bindings['open_cfw_gx8002_tws_audio_message']=0x1020b250
    script=out/'tws-audio.ld';script.write_text('SECTIONS { .text 0x100263dc : { *(.text.open_cfw_gx8002_tws_audio_callback) } .state 0x2002e740 (NOLOAD) : { *(.bss.tws_audio_last_vad) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    path=out/'tws-audio.elf';subprocess.run([pre+'ld','-T',str(script),*(str(o) for o in objects),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'audio');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==2
    state=next(s for s in sections if s['name']=='.state');assert (state['address'],state['size'],state['type'],state['flags'])==(0x2002e740,4,8,3)
    text=next(s for s in sections if s['name']=='.text');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert text['address']==0x100263dc and text['size']<=248
    owner_path=ROOT/'build/gx8002-source-candidate/runtime-messages/runtime-messages.elf';owner=Elf32(owner_path.read_bytes(),'messages')
    owner_report=json.loads((ROOT/'docs/research/gx8002-runtime-messages-source-verification.json').read_text());row=next(r for r in owner_report['functions'] if r['section_name']=='.rodata.tws');message=next(s for s in owner.sections if s['name']=='.rodata.tws');message_data=owner.contents(message)
    assert sha(message_data)==row['compiled_sha256'] and message['address']==0x1020b230
    diagnostic=b'[LVP_TWS]Ctx:%d, Vad:%d, Ns:%d, R:%d\n\0'
    assert message_data[32:]==diagnostic==stock[0x147dc:0x14802]
    assert not any(elf.relocations(s['index']) for s in sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'tws-audio.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    r={'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sources,'flags':flags,'bindings':bindings,'elf_sha256':sha(path.read_bytes()),'compiled_bytes':text['size'],'compiled_sha256':sha(elf.contents(text)),'message_bytes':len(diagnostic),'message_sha256':sha(diagnostic),'message_owner_elf_sha256':sha(owner_path.read_bytes()),'source_admitted':False,'limits':['Linked source fits including its own pointer literals; existing shared pool outside body preserved. Empty register constraint retains hardware division. Last-VAD source BSS allocated; behavior/integration/ownership evidence reviewed separately. Source admission pending.']};(ROOT/'docs/research/gx8002-tws-audio-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(build()['compiled_bytes'])
