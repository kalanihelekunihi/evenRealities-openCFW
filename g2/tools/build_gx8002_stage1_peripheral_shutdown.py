# SPDX-License-Identifier: MIT
"""Build complete peripheral shutdown C at its BINH stage-one entry."""
import json,subprocess
from build_gx8002_backup_loader import build as loader
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32,IMAGE,IMAGE_SHA


def build():
    mapping=loader();base=mapping['mapping_vector_package_offset'];address=lambda off:off-base+0x10000000
    out=ROOT/'build/gx8002-stage1-peripheral-shutdown';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_peripheral_shutdown.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'state.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
    ld=out/'state.ld';ld.write_text(f'SECTIONS {{ .text {address(0x39b88):#x} : {{ *(.text*) *(.rodata*) }} }}\nopen_cfw_gx8002_stage1_gate = {address(0x38b4c):#x};\n')
    path=out/'state.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'state');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    section=next(s for s in elf.sections if s['name']=='.text');size=section['size']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert size==42 and elf.contents(section)==stock[0x39b88:0x39bb2]
    (out/'state.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'stock_identical':True,'code_bytes':size,'envelope_bytes':44,'fits':size<=44,'source_admitted':False,'limits':['Complete C peripheral shutdown; module gate remains absolute. Behavioral comparison and source integration pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-stage1-peripheral-shutdown.json').write_text(json.dumps(r,indent=2)+'\n');print(r['code_bytes'],'peripheral shutdown source bytes; fits:',r['fits'])
