# SPDX-License-Identifier: MIT
"""Build the recovered application command registration."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-app-command-callback';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_app_command_callback.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_command_state': 537061616, 'open_cfw_gx8002_command_response': 537029980, 'open_cfw_gx8002_app_reply': 270570484, 'open_cfw_gx8002_command_enqueue': 270566332, 'open_cfw_gx8002_command_mic': 270562308, 'open_cfw_gx8002_command_gsensor': 270559496, 'open_cfw_gx8002_command_direction': 270556964, 'open_cfw_gx8002_command_beamforming': 270563968, 'open_cfw_gx8002_command_gain': 270549932, 'open_cfw_gx8002_command_padmux': 270558684, 'open_cfw_gx8002_command_delay': 270551472, 'strtok': 270571868, 'printf': 270560292}
    diagnostics={'mic': 270579509, 'gsensor': 270579532, 'version': 270579558, 'delimiter': 270579579, 'beamforming': 270579581, 'vad_open': 270579604, 'vad_close': 270579624, 'byte': 270579645, 'gain_ok': 270579652, 'gain_fail': 270579677, 'gain_range': 270579699, 'dmic_open': 270579739, 'dmic_init': 270579762, 'dmic_close': 270579780, 'dmic_stop': 270579804, 'delay': 270579823, 'i2s': 270579853, 'mode': 270579881}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10209430 : { *(.text.open_cfw_gx8002_app_command_callback) } '+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_callback_{n}) }} ' for n,a in diagnostics.items())+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    for n,a in diagnostics.items():
        s=next(s for s in elf.sections if s['name']=='.rodata.'+n);data=elf.contents(s);offset=a-0x101f6a74
        if s['address']!=a or data!=stock[offset:offset+len(data)] or elf.relocations(s['index']):raise ValueError('Diagnostic')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':716,'stock_sha256':sha(stock[0x129bc:0x12c88]),'fits':section['size']<=716,'source_admitted':False,'limits':['Application commands candidate only; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-app-command-callback-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
