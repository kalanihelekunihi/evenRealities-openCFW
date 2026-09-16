# SPDX-License-Identifier: MIT
"""Compile complete stage-one UART setup with explicit arithmetic dependencies."""
import json,subprocess
from build_gx8002_backup_loader import build as loader
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32


def build():
    mapping=loader();base=mapping['mapping_vector_package_offset'];address=lambda off:off-base+0x10000000
    out=ROOT/'build/gx8002-stage1-uart-configure';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_uart_configure.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'uart.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
    bindings={'open_cfw_gx8002_stage1_frequency':0x38c54,'open_cfw_gx8002_stage1_39774':0x39774,'open_cfw_gx8002_stage1_397b8':0x397b8}
    ld=out/'uart.ld';ld.write_text(f'SECTIONS {{ .text {address(0x39bb4):#x} : {{ *(.text*) *(.rodata*) }} }}\n'+''.join(f'{name} = {address(off):#x};\n' for name,off in bindings.items()))
    path=out/'uart.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'uart');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    size=next(s['size'] for s in elf.sections if s['name']=='.text')
    (out/'uart.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'code_bytes':size,'envelope_bytes':128,'fits':size<=128,'bindings':bindings,'source_admitted':False,'limits':['Complete readable UART setup C; original arithmetic helper calls and wraparound retained. Frequency and arithmetic are absolute dependencies. Decoded comparison, polling qualification, placement and integration pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-stage1-uart-configure.json').write_text(json.dumps(r,indent=2)+'\n');print(r['code_bytes'],'UART source bytes; fits:',r['fits'])
