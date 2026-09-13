# SPDX-License-Identifier: MIT
"""Build source-defined mutable playback settings and their selector."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw_config.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Settings stock identity')
    upstream=next(s for s in oracle.sections if s['name']=='.text.aout_select_hw_config');text=oracle.contents(upstream)
    if len(text)!=8 or text[:4]!=stock[0xe900:0xe904] or [(r['offset'],r['type']) for r in oracle.relocations(upstream['index'])]!=[(4,1)]:raise ValueError('Selector identity')
    if int.from_bytes(stock[0xe904:0xe908],'little')!=0x20026c1c:raise ValueError('Settings stock pointer')
    original=oracle.contents(next(s for s in oracle.sections if s['name']=='.data'))
    if len(original)!=84 or original!=stock[0x18c30:0x18c84]:raise ValueError('SDK settings identity')
    out=ROOT/'build/gx8002-audio-output-hw-config';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_hw_config.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    (out/'bits.ld').write_text('SECTIONS { .text.aout_select_hw_config 0x10205374 : { *(.text*) } .data.aout_hw_settings 0x20026c1c : { *(.data*) } }\n')
    subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True);elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf')
    if any(s['size'] and s['flags']&2 and s['name'] not in ('.text.aout_select_hw_config','.data.aout_hw_settings') for s in elf.sections):raise ValueError('Unaccounted settings section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved settings link')
    rows=[]
    for symbol,name,offset,size,kind in (('aout_select_hw_config','.text.aout_select_hw_config',0xe900,8,'compiled_c'),('aout_hw_settings','.data.aout_hw_settings',0x18c30,84,'generated_source_data')):
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section)
        if payload!=stock[offset:offset+size]:raise ValueError('Source settings/selector bytes differ')
        if kind=='generated_source_data' and not section['flags']&1:raise ValueError('Settings must be writable')
        rows.append({'symbol':'open_cfw_gx8002_'+symbol,'section_name':name,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'ownership_kind':kind,'fits':True})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data)},'source_admitted':False,'hardware_qualified':False,'limits':['Source-defined typed settings reproduce pinned SDK and stock initialization. Some field hardware meanings remain unresolved; this is not whole-source closure.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-hw-config-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
