# SPDX-License-Identifier: MIT
"""Build reconstructed PDM setup with authenticated SDK relocation names."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_in/v2.0/audio_in.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    oracle=authenticated_blob(sdk/rel,blob);oe=Elf32(oracle,rel)
    section=next(s for s in oe.sections if s['name']=='.text.gx_audio_in_set_input_pdm')
    relocations=oe.relocations(section['index'])
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_input_pdm.c'
    out=ROOT/'build/gx8002-audio-input-pdm';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'pdm.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    bindings={'open_cfw_gx8002_platform_gate':0x10025080,'open_cfw_gx8002_audio_input_state':0x20027330,'gx_mdelay':0x1002598c}
    script=out/'pdm.ld';script.write_text('SECTIONS { .text 0x10203e7c : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    target=out/'pdm.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    e=Elf32(target.read_bytes(),str(target));text=next(s for s in e.sections if s['name']=='.text');payload=e.contents(text)
    if any(e.relocations(s['index']) for s in e.sections) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('PDM unresolved link')
    (out/'pdm.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('PDM stock identity')
    return {'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'section':section['name'],'relocations':relocations,'role':'symbol_evidence_only'},'bindings':bindings,
        'source_sha256':sha(source.read_bytes()),
        'symbol':'open_cfw_gx8002_audio_input_pdm','compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0xd408,'stock_envelope_bytes':76,'stock_sha256':sha(stock[0xd408:0xd454]),'fits':len(payload)<=76,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-input-pdm-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],r['fits'])
