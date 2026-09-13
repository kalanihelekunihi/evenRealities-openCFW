# SPDX-License-Identifier: MIT
"""Build recovered upstream-layout audio-input environmental noise query on native macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('include/lvp_context.h','include/lvp_attr.h','include/lvp_param.h','include/driver/gx_audio_in.h','include/driver/gx_audio_in/gx_audio_in_v2.h','include/driver/gx_padmux.h','lvp/common/lvp_audio_in.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-audio-input-env-noise';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_input_env_noise.c';flags=['-Os',*FLAGS[1:]]
    config=out/'autoconf.h';config.write_text('#define CONFIG_ARCH_GRUS 1\n')
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-I',str(sdk/'include'),'-c',str(source),'-o',str(out/'index.o')],check=True)
    bindings={'gx_audio_in_get_distance_noise_smooth':0xdd38}
    script='SECTIONS { .text 0x102075c8 : { *(.text.open_cfw_gx8002_audio_input_env_noise) } }\n'
    script+=''.join(name+' = '+hex(offset+0x101f6a74)+';\n' for name,offset in bindings.items())
    script+='memcpy = 0x10025738;\n'
    (out/'index.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),'-o',str(out/'index.elf')],check=True)
    elf=Elf32((out/'index.elf').read_bytes(),'index');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unowned allocation')
    disassembly=subprocess.check_output([pre+'objdump','-d',str(out/'index.elf')],text=True)
    (out/'index.disassembly.txt').write_text(disassembly)
    from verify_gx8002_memcpy_source import decode
    code=decode(disassembly)
    call_targets=[int(args,0) for op,args,width in code.values() if op=='bsr']
    expected={offset+0x101f6a74 for offset in bindings.values()}
    if set(call_targets)!=expected:raise ValueError('Missing or unexpected helper target')

    return {'compiled_bytes':len(payload),'fits':len(payload)<=124,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x10b54:0x10bd0]),'exact_stock':payload==stock[0x10b54:0x10bd0],'source_sha256':sha(source.read_bytes()),'flags':flags,'upstream':upstream,'configuration_sha256':sha(config.read_bytes()),'bindings':bindings,'decoded_call_targets':call_targets,'source_admitted':False}
if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-audio-input-env-noise-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes'])
