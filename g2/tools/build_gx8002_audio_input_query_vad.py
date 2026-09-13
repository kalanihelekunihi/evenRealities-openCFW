# SPDX-License-Identifier: MIT
"""Build recovered upstream-layout audio-input VAD query on native macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('include/lvp_param.h','include/driver/gx_audio_in.h','include/driver/gx_audio_in/gx_audio_in_v2.h','include/driver/gx_padmux.h','lvp/common/lvp_audio_in.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-audio-input-query-vad';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_input_query_vad.c';flags=['-Os',*FLAGS[1:]]
    config=out/'autoconf.h';config.write_text('#define CONFIG_ARCH_GRUS 1\n')
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-I',str(sdk/'include'),'-c',str(source),'-o',str(out/'index.o')],check=True)
    diagnostic_source=ROOT/'components/shared/gx8002/runtime_gx8002_vad_diagnostics.c'
    subprocess.run([pre+'gcc',*flags,'-c',str(diagnostic_source),'-o',str(out/'diagnostics.o')],check=True)
    bindings={'gx_audio_in_get_distance_noise_smooth':0xdd38,'printf':0x101b0,
              'gx_audio_in_set_fftvad_curve_1':0xdbbc,'gx_audio_in_set_fftvad_curve_2':0xdbf0,
              'gx_audio_in_set_fftvad_curve_3':0xdc24,'gx_audio_in_set_fftvad_curve_4':0xdc64,
              'gx_audio_in_set_fftvad_curve_5':0xdc98,'gx_audio_in_set_fftvad_chipping':0xdcb8,
              'gx_audio_in_set_fftvad_w':0xdb80,'gx_audio_in_get_fftvad_state':0xdd08}
    script='SECTIONS { .text 0x10207404 : { *(.text.open_cfw_gx8002_audio_input_query_vad) }\n'

    diagnostics=[]
    for level,offset in ((4,0x143a0),(3,0x143bb),(2,0x143d6),(1,0x143f1)):
        message=('[LVP_AUD]vad param '+str(level)+' [%d]\n').encode()+b'\0'
        if stock[offset:offset+len(message)]!=message:raise ValueError('Diagnostic text')
        diagnostics.append({'level':level,'package_offset':offset,'bytes':len(message),'sha256':sha(message)})
        symbol='open_cfw_vad_level_'+str(level)+'_message'
        script+='.rodata.level'+str(level)+' '+hex(offset+0x101f6a74)+' : { *(.rodata.'+symbol+') }\n'

    script+='}\n'+''.join(name+' = '+hex(offset+0x101f6a74)+';\n' for name,offset in bindings.items())
    (out/'index.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),str(out/'diagnostics.o'),'-o',str(out/'index.elf')],check=True)
    elf=Elf32((out/'index.elf').read_bytes(),'index');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name'] not in ('.text','.rodata.level1','.rodata.level2','.rodata.level3','.rodata.level4') for s in elf.sections):raise ValueError('Unowned allocation')
    for row in diagnostics:
        section=next(s for s in elf.sections if s['name']=='.rodata.level'+str(row['level']))
        if elf.contents(section)!=stock[row['package_offset']:row['package_offset']+row['bytes']]:raise ValueError('Linked diagnostic')
    disassembly=subprocess.check_output([pre+'objdump','-d',str(out/'index.elf')],text=True)
    (out/'index.disassembly.txt').write_text(disassembly)
    from verify_gx8002_memcpy_source import decode
    code=decode(disassembly)
    call_targets=[int(args,0) for op,args,width in code.values() if op=='bsr']
    expected={offset+0x101f6a74 for offset in bindings.values()}
    if set(call_targets)!=expected:raise ValueError('Missing or unexpected helper target')

    return {'compiled_bytes':len(payload),'fits':len(payload)<=452,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x10990:0x10b54]),'exact_stock':payload==stock[0x10990:0x10b54],'source_sha256':sha(source.read_bytes()),'flags':flags,'upstream':upstream,'configuration_sha256':sha(config.read_bytes()),'bindings':bindings,'diagnostics':diagnostics,'diagnostic_source_sha256':sha(diagnostic_source.read_bytes()),'decoded_call_targets':call_targets,'source_admitted':False}
if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-audio-input-query-vad-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes'])
