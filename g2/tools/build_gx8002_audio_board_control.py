# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ROWS=[('get',0xc590,8),('gain',0xc598,24),('init',0xc5b0,44)]
def build():
    out=ROOT/'build/gx8002-audio-board-control';out.mkdir(exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_board_control.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    script='SECTIONS {\n'+''.join(f'.text.{n} {o+0x101f6a74:#x} : {{ *(.text.open_cfw_audio_board_{n}) }}\n' for n,o,_ in ROWS)+'}\nopen_cfw_audio_board_state = 0x200269a4;\nopen_cfw_dmic_channels = 0x1020a8b3;\nopen_cfw_dmic_gain = 0x1020a8d3;\nprintf = 0x10206c24;\n'
    (out/'candidate.ld').write_text(script);subprocess.run([pre+'ld','-T',str(out/'candidate.ld'),str(out/'candidate.o'),'-o',str(out/'candidate.elf')],check=True)
    e=Elf32((out/'candidate.elf').read_bytes(),'board');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    assert len([s for s in e.sections if s['flags']&2 and s['size']])==3
    for n,o,size in ROWS:
        s=next(s for s in e.sections if s['name']=='.text.'+n);data=e.contents(s);assert s['address']==o+0x101f6a74 and len(data)<=size and not e.relocations(s['index'])
        rows.append({'symbol':'open_cfw_audio_board_'+n,'section_name':s['name'],'ownership_kind':'compiled_c','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':'open_cfw_audio_board_'+n,'package_offset':o,'bytes':size,'sha256':sha(stock[o:o+size]),'region':'image_a_xip_text'}]})
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'candidate.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes())}
if __name__=='__main__':print(json.dumps(build(),indent=2))
