# SPDX-License-Identifier: MIT
"""Build the recovered keyword strategy selection candidate."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-kws-strategy';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_strategy.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_activations':0x2002e7a8,'open_cfw_gx8002_max_keyword_list':0x2002e79c,'printf':0x10206c24}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10208a10 : { *(.text.open_cfw_gx8002_kws_strategy) *(.text*) } .rodata.row 0x1020b37e : { *(.rodata.open_cfw_gx8002_strategy_row) } .rodata.selected 0x1020b39f : { *(.rodata.open_cfw_gx8002_strategy_selected) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if stock[0x184f0:0x184f8]!=bytes.fromhex('01103c789ce70220'):raise ValueError('Parameter helper changed')
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':328,'stock_sha256':sha(stock[0x11f9c:0x120e4]),'fits':section['size']<=328,'source_admitted':False,'limits':['Constant-return parameter helper folded into source reference after authenticating exact leaf instructions. Selection behavior and ABI still need qualification.']}
    (ROOT/'docs/research/gx8002-kws-strategy-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
