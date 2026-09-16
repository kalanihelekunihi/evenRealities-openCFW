# SPDX-License-Identifier: MIT
"""Build complete boot-state selection C at its BINH stage-one entry."""
import json,subprocess
from build_gx8002_backup_loader import build as loader
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32


def build():
    mapping=loader();base=mapping['mapping_vector_package_offset'];address=lambda off:off-base+0x10000000
    out=ROOT/'build/gx8002-stage1-boot-state';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_boot_state.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'state.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
    ld=out/'state.ld';ld.write_text(f'SECTIONS {{ .text {address(0x39678):#x} : {{ *(.text*) *(.rodata*) }} }}\nopen_cfw_gx8002_stage1_39b88 = {address(0x39b88):#x};\n')
    path=out/'state.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'state');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    size=next(s['size'] for s in elf.sections if s['name']=='.text')
    (out/'state.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'code_bytes':size,'envelope_bytes':40,'fits':size<=40,'source_admitted':False,'limits':['Complete C mode/offset selection; initial hardware helper remains absolute. Behavioral comparison and source integration pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-stage1-boot-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['code_bytes'],'boot-state source bytes; fits:',r['fits'])
