# SPDX-License-Identifier: MIT
"""Build explicit volume mapping and setter/getter source candidates."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Volume stock identity')
    for name,offset,size,reloc in (('aout_set_db',0xe51c,96,92),('aout_get_db',0xe57c,60,56)):
        section=next(s for s in oracle.sections if s['name']=='.text.'+name);upstream=oracle.contents(section)
        if len(upstream)!=size or upstream[:reloc]!=stock[offset:offset+reloc] or [(r['offset'],r['type']) for r in oracle.relocations(section['index'])]!=[(reloc,1)]:raise ValueError('Volume SDK identity')
        if int.from_bytes(stock[offset+reloc:offset+reloc+4],'little')!=0x1020a910:raise ValueError('Volume table pointer')
    table=oracle.contents(next(s for s in oracle.sections if s['name']=='.rodata'))[28:176]
    if table!=stock[0x13e9c:0x13f30] or stock[0x13f32:0x13f34]!=b'\1\0':raise ValueError('Volume mapping or miss result')
    out=ROOT/'build/gx8002-audio-output-volume';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_volume.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    entries=(('aout_set_db',0xe51c,96,'compiled_c'),('aout_get_db',0xe57c,60,'compiled_c'),('aout_gain_steps',0x13e9c,148,'generated_source_data'))
    script='SECTIONS {\n'
    for name,offset,size,kind in entries:
        section='.rodata.' if kind=='generated_source_data' else '.text.';script+=f'{section}{name} {offset+0x101f6a74:#x} : {{ *({section}open_cfw_gx8002_{name}) }}\n'
    (out/'bits.ld').write_text(script+'}\n');subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True);elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    allowed={('.rodata.' if k=='generated_source_data' else '.text.')+n for n,o,z,k in entries}
    if any(s['size'] and s['flags']&2 and s['name'] not in allowed for s in elf.sections):raise ValueError('Volume unaccounted section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Volume unresolved link')
    for name,offset,size,kind in entries:
        section=('.rodata.' if kind=='generated_source_data' else '.text.')+name;payload=elf.contents(next(s for s in elf.sections if s['name']==section))
        if kind=='generated_source_data' and payload!=table:raise ValueError('Source gain mapping differs')
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':section,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'ownership_kind':kind,'fits':len(payload)<=size})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data)},'source_admitted':False,'hardware_qualified':False,'limits':['Explicit fallback1 replaces stock out-of-bounds table read. Decoded access order, aliasing and full signed input behavior remain to qualify.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-volume-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
