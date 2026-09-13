# SPDX-License-Identifier: MIT
"""Build reconstructed FFTVAD curve1 setup with authenticated SDK relocation names."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_in/v2.0/audio_in.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    oracle=authenticated_blob(sdk/rel,blob);oe=Elf32(oracle,rel)
    section=next(s for s in oe.sections if s['name']=='.text.gx_audio_in_set_fftvad_curve_1')
    relocations=oe.relocations(section['index'])
    header='include/driver/gx_audio_in/gx_audio_in_v2.h'
    header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,header_blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_fftvad_curve1.c'
    out=ROOT/'build/gx8002-audio-fftvad-curve1';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'gain.o'
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    bindings={}
    script=out/'gain.ld';script.write_text('SECTIONS { .text 0x10204630 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    target=out/'gain.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    e=Elf32(target.read_bytes(),str(target));text=next(s for s in e.sections if s['name']=='.text');payload=e.contents(text)
    if any(e.relocations(s['index']) for s in e.sections) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('FFTVAD curve1 unresolved link')
    (out/'gain.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('PGA gain stock identity')
    return {'sdk_commit':SDK_COMMIT,'header':{'path':header,'blob':header_blob},'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'section':section['name'],'relocations':relocations,'role':'symbol_evidence_only'},'bindings':bindings,
        'source_sha256':sha(source.read_bytes()),
        'symbol':'open_cfw_gx8002_audio_fftvad_curve1','compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0xdbbc,'stock_envelope_bytes':52,'stock_sha256':sha(stock[0xdbbc:0xdbf0]),'fits':len(payload)<=52,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-fftvad-curve1-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],r['fits'])
