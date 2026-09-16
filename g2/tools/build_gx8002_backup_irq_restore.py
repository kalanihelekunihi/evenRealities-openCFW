# SPDX-License-Identifier: MIT
"""Build a symbolic BSS object and its reconstructed interrupt restore reader."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,FLAGS


def build():
    out=ROOT/'build/gx8002-backup-irq-restore';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_irq_restore.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'restore.o';cmd=[pre+'gcc',*FLAGS,'-Os','-c',str(source),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    ld=out/'restore.ld';ld.write_text('SECTIONS { .text 0x1000482c : { *(.text*) } .saved 0x200173a0 (NOLOAD) : { *(.bss.backup_irq_saved) } }\n')
    path=out/'restore.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'IRQ restore')
    text=next(s for s in elf.sections if s['name']=='.text');saved=next(s for s in elf.sections if s['name']=='.saved')
    assert saved['address']==0x200173a0 and saved['size']==8 and saved['type']==8
    assert text['address']==0x1000482c and text['size']<=24
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'restore.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'source_sha256':sha(source.read_bytes()),'command':cmd,'elf_sha256':sha(path.read_bytes()),'code_bytes':text['size'],'stock_envelope_bytes':24,'bss_address':saved['address'],'bss_bytes':8,'source_admitted':False,'limits':['Symbolic two-word BSS allocation at original address and complete reader; other accesses, behavioral/reference verification and integration pending. No memory map moved.']}
    (ROOT/'docs/research/gx8002-backup-irq-restore.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
