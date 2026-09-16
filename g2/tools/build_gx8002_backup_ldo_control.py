# SPDX-License-Identifier: MIT
"""Build complete recovered digital LDO control C on macOS."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-ldo-control';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_backup_ldo_control.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'ldo.o';subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
    ld=out/'ldo.ld';ld.write_text('SECTIONS { .text 0x100080f4 : { *(.text*) *(.rodata*) } }\n')
    path=out/'ldo.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'ldo');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    sec=next(s for s in elf.sections if s['name']=='.text')
    (out/'ldo.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'code_bytes':sec['size'],'stock_envelope':64,'fits':sec['size']<=64,'source_admitted':False}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-ldo-control.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
