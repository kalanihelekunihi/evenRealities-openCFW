# SPDX-License-Identifier: MIT
"""Build reconstructed SADC setup with authenticated SDK relocation names."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_in/v2.0/audio_in.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    oracle=authenticated_blob(sdk/rel,blob);oe=Elf32(oracle,rel)
    section=next(s for s in oe.sections if s['name']=='.text.gx_audio_in_set_input_sadc')
    relocations=oe.relocations(section['index'])
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_input_sadc.c'
    out=ROOT/'build/gx8002-audio-input-sadc';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'sadc.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    offsets={'gx_analog_set_adc_rstn':0xf454,'gx_analog_set_pga_bypass':0xf3dc,'gx_analog_set_pga_enable':0xf3f4,'gx_analog_set_adc_sample_clk_sel':0xf40c,'gx_analog_set_adc_out_at_clk':0xf424,'gx_analog_set_adc_in_sel':0xf43c,'gx_analog_set_pga_itrim':0xf3c0}
    bindings={name:offset+0x101f6a74 for name,offset in offsets.items()}
    bindings.update(open_cfw_gx8002_platform_gate=0x10025080,open_cfw_gx8002_audio_input_state=0x20027330)
    script=out/'sadc.ld';script.write_text('SECTIONS { .text 0x10203e18 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    target=out/'sadc.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    e=Elf32(target.read_bytes(),str(target));text=next(s for s in e.sections if s['name']=='.text');payload=e.contents(text)
    if any(e.relocations(s['index']) for s in e.sections) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('SADC unresolved link')
    (out/'sadc.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('SADC stock identity')
    return {'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'section':section['name'],'relocations':relocations,'role':'symbol_evidence_only'},'bindings':bindings,
        'source_sha256':sha(source.read_bytes()),'header_sha256':sha(source.with_name('runtime_gx8002_analog.h').read_bytes()),
        'symbol':'open_cfw_gx8002_audio_input_sadc','compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0xd3a4,'stock_envelope_bytes':100,'stock_sha256':sha(stock[0xd3a4:0xd408]),'fits':len(payload)<=100,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-input-sadc-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],r['fits'])
