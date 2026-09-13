# SPDX-License-Identifier: MIT
"""Build recovered hardware-logfbank audio callback using pinned SDK headers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha,IMAGE,IMAGE_SHA
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('include/lvp_context.h','include/lvp_attr.h','lvp/common/lvp_audio_in.c','lvp/common/lvp_audio_in.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);deps.append({'path':rel,'blob':blob,'sha256':sha(data)})
    config=out/'audio-record-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_record_callback.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap','-fira-algorithm=priority']
    obj=out/'audio-record.o';subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
    bindings={name:address+0x1000dfec for name,address in {
        'LvpAudioInQueryFFTVad':0x1f9418,'LvpGetContextHeader':0x1f8eb0,
        'LvpGetLogfbankFrameNumPerChannel':0x1f8f88,'LvpGetPcmFrameNumPerContext':0x1f8f64,
        'LvpGetContextNum':0x1f8f98,'LvpGetContextGap':0x1f8f94}.items()}
    state={"control":(0x2002ecb0,20),"handler":(0x2002dfa0,4),"invalid_vad":(0x2002dfa8,4)}
    script=out/'audio-record.ld';script.write_text('SECTIONS { .text 0x10026214 : { *(.text.open_cfw_gx8002_audio_record_callback) } '+''.join(f'.audio_record_{n} {a:#x} (NOLOAD) : {{ *(.bss.audio_record_{n}) }} ' for n,(a,size) in state.items())+'}\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    path=out/'audio-record.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'audio record');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==4
    for name,(address,size) in state.items():
        item=next(s for s in sections if s['name']=='.audio_record_'+name)
        assert (item['address'],item['size'],item['type'],item['flags'])==(address,size,8,3)
    section=next(s for s in sections if s['name']=='.text');assert section['address']==0x10026214 and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'audio-record.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'bindings':bindings,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_offset':0x18228,'stock_bytes':256,'stock_sha256':sha(stock[0x18228:0x18328]),'fits':section['size']<=256,'runtime_state':{n:{'address':a,'bytes':size,'type':'NOBITS'} for n,(a,size) in state.items()},'source_admitted':False,'limits':['Compiled and linked only; decoded behavior, callback/control storage ownership and physical execution pending.']}
    (ROOT/'docs/research/gx8002-audio-record-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['compiled_bytes'])
