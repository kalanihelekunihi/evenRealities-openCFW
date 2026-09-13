# SPDX-License-Identifier: MIT
"""Build the recovered sample app initialization."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-sample-app-init';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_sample_app_init.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_sample_state':0x2002e8c4,'open_cfw_gx8002_sample_setup':0x102096fc,'open_cfw_gx8002_power_lock_create':0x10207770,'printf':0x10206c24}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10208e4c : { *(.text.open_cfw_gx8002_sample_app_init) } .rodata.name 0x1020b419 : { *(.rodata.open_cfw_gx8002_sample_init_name) } .rodata.message 0x1020b458 : { *(.rodata.open_cfw_gx8002_sample_init_message) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':52,'stock_sha256':sha(stock[0x123d8:0x1240c]),'fits':section['size']<=52,'source_admitted':False,'limits':['SampleAppInit candidate: setup helper identity, guard/order, diagnostic and ABI qualification pending.']}
    (ROOT/'docs/research/gx8002-sample-app-init-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
