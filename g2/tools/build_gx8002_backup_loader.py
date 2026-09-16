# SPDX-License-Identifier: MIT
"""Compile and link complete backup-loader C at its BINH stage-one mapping."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32,IMAGE,IMAGE_SHA


def build():
    out=ROOT/'build/gx8002-backup-loader';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_backup_loader.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'loader.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'loader object')
    undefined=[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]
    assert undefined==['open_cfw_gx8002_loader_flash_read'],undefined
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    (out/'loader.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(path)],text=True))
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    base=0x3893c+24
    assert stock[0x3893c:0x38940]==b'BINH'
    vectors=[int.from_bytes(stock[base+i:base+i+4],'little') for i in range(0,256,4)]
    assert vectors==[0x10000100]+[0x10000130]*63
    entry=0x396a0-base+0x10000000;helper=0x39930-base+0x10000000
    ld=out/'loader.ld';ld.write_text(f'SECTIONS {{ .text {entry:#x} : {{ *(.text*) *(.rodata*) }} }}\nopen_cfw_gx8002_loader_flash_read = {helper:#x};\n')
    linked=out/'loader.elf';subprocess.run([pre+'ld','-T',str(ld),str(path),'-o',str(linked)],check=True)
    final=Elf32(linked.read_bytes(),'linked loader')
    assert not any(s['name'] and s['section']==0 for s in final.symbols())
    assert not any(final.relocations(s['index']) for s in final.sections)
    (out/'loader.linked.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))
    return {'entry_address':entry,'helper_address':helper,'mapping_vector_package_offset':base,'elf_sha256':sha(linked.read_bytes()),'source_sha256' :sha(src.read_bytes()),'object_sha256':sha(path.read_bytes()),'allocated_bytes':sum(s['size'] for s in sections),'undefined_symbols':undefined,'source_admitted':False,'limits':['Complete C loader control compiled as a relocatable object on macOS. Linked execution addresses follow the authenticated BINH stage-one vector mapping. Decoded source comparison and integration remain pending; the flash helper remains an absolute dependency. The helper dependency is not stubbed or represented as binary data.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-loader.json').write_text(json.dumps(r,indent=2)+'\n');print(r['allocated_bytes'],'loader object bytes')
