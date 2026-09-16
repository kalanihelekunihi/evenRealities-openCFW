# SPDX-License-Identifier: MIT
"""Reuse recovered trim-state C at the backup image entry."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    out=ROOT/'build/gx8002-backup-trim-state';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_trim_state.c'
    unit=out/'trim.c'
    # Backup performs the gate call inline; image A has a separate gate wrapper.
    body=source.read_text().replace('extern void open_cfw_gx8002_trim_clock_enable(void);','extern void gx_clock_set_module_enable(unsigned int, unsigned int);\nstatic inline void open_cfw_gx8002_trim_clock_enable(void) { gx_clock_set_module_enable(9, 1); }')
    unit.write_text(body)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'trim.o';subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(unit),'-o',str(obj)],check=True)
    ld=out/'trim.ld';ld.write_text('SECTIONS { .text 0x1000401c : { *(.text*) } }\ngx_clock_set_module_enable = 0x10003be8;\n')
    path=out/'trim.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trim');sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert len(data)==22 and data==stock[0x3c95c:0x3c972]
    assert next(s['value'] for s in elf.symbols() if s['name']=='gx_clock_set_module_enable')==0x3c528-0x3b940+0x10003000
    (out/'trim.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'source_sha256':sha(source.read_bytes()),'adapted_source_sha256':sha(unit.read_bytes()),'elf_sha256':sha(path.read_bytes()),'package_offset':0x3c95c,'bytes':len(data),'stock_identical':True,'source_admitted':False,'limits':['Complete source trim reader matches stock instructions exactly, including gate-call target. Gate implementation remains an absolute dependency; source ownership not yet integrated.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-trim-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['bytes'],'byte-identical source trim bytes')
