# SPDX-License-Identifier: MIT
"""Native source candidate for the unnamed indexed audio field helper."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Audio field stock identity')
    out=ROOT/'build/gx8002-audio-channel-field';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_channel_field.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'field.o')],check=True)
    (out/'field.ld').write_text('SECTIONS { .text 0x102049b0 : { *(.text*) } }\n')
    subprocess.run([pre+'ld','-T',str(out/'field.ld'),str(out/'field.o'),'-o',str(out/'field.elf')],check=True)
    elf=Elf32((out/'field.elf').read_bytes(),'field.elf')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved field link')
    data=elf.contents(next(s for s in elf.sections if s['name']=='.text'))
    (out/'field.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'field.elf')],text=True))
    return {'symbol':'open_cfw_gx8002_audio_channel_field','compiled_bytes':len(data),'compiled_sha256':sha(data),'source_sha256':sha(source.read_bytes()),'package_offset':0xdf3c,'stock_envelope_bytes':24,'stock_sha256':sha(stock[0xdf3c:0xdf54]),'fits':len(data)<=24,'source_admitted':False,'hardware_qualified':False,'provenance':'Recovered stock instructions; SDK drivers_lib object text scan found no exact match. Semantic API name unresolved.'}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-channel-field-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],r['fits'])
