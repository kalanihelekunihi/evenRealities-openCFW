# SPDX-License-Identifier: MIT
"""Build the recovered sample event dispatcher."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-sample-event';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_sample_event.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/app_core')]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_event_state':0x20026d30,'open_cfw_gx8002_event_app':0x2002e8c4,'open_cfw_gx8002_context_lookup':0x10206ec8,'open_cfw_gx8002_vad_notify':0x1020979c,'open_cfw_gx8002_event_notify':0x1020975c,'open_cfw_gx8002_mic_buffer':0x10208e80,'open_cfw_gx8002_audio_frame':0x10205488,'printf':0x10206c24}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10208f04 : { *(.text.open_cfw_gx8002_sample_event) } .rodata.hey 0x1020b4c7 : { *(.rodata.open_cfw_gx8002_event_hey) } .rodata.hi 0x1020b4d9 : { *(.rodata.open_cfw_gx8002_event_hi) } .rodata.start 0x1020b4ea : { *(.rodata.open_cfw_gx8002_event_start) } .rodata.range 0x1020b50a : { *(.rodata.open_cfw_gx8002_event_range) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':236,'stock_sha256':sha(stock[0x12490:0x1257c]),'fits':section['size']<=236,'source_admitted':False,'limits':['Event candidate only; source diagnostics defined, helper mutations, ignored errors and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-sample-event-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
