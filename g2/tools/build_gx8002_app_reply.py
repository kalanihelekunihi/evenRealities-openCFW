# SPDX-License-Identifier: MIT
"""Build the recovered application response helper."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-app-reply';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_app_reply.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-store-merging','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common')]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_app_reply_state':0x20026d5c,'open_cfw_gx8002_app_reply_value':0x2002e914,'open_cfw_gx8002_app_enqueue':0x102083bc}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x102093f4 : { *(.text.open_cfw_gx8002_app_reply) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':60,'stock_sha256':sha(stock[0x12980:0x129bc]),'fits':section['size']<=60,'source_admitted':False,'limits':['Reply candidate only; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-app-reply-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
