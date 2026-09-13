# SPDX-License-Identifier: MIT
"""Link source backup DMA routines together; relocation candidate only."""
import json,subprocess
from build_gx8002_backup_dma_deallocate import build as deallocate,ROOT,Elf32,sha
from build_gx8002_backup_dma_irq import build as irq
from build_gx8002_backup_dma_initialize import build as initialize

def build():
    builds={'deallocate':deallocate(),'irq':irq(),'initialize':initialize()}
    out=ROOT/'build/gx8002-backup-dma-combined';out.mkdir(exist_ok=True)
    script=out/'combined.ld'
    script.write_text('''SECTIONS {
      .deallocate 0x10004bc0 : { *(.text.open_cfw_gx8002_backup_dma_deallocate) }
      .irq ALIGN(4) : { *(.text.open_cfw_gx8002_backup_dma_irq_handler) }
      ASSERT(. <= 0x10004c7c, "DMA pair overflows")
      .initialize 0x10004d14 : { *(.text.open_cfw_gx8002_dma_initialize) }
      ASSERT(. <= 0x10004d94, "DMA initializer overflows")
    }
    open_cfw_gx8002_backup_dma_state = 0x2002d3e8;
    open_cfw_gx8002_dma_state = open_cfw_gx8002_backup_dma_state;
    open_cfw_gx8002_backup_dma_callbacks = 0x200174a8;
    open_cfw_gx8002_backup_irq_save = 0x1000486c;
    open_cfw_gx8002_backup_irq_restore = 0x10004878;
    open_cfw_gx8002_backup_dma_resource = 0x10003be8;
    open_cfw_gx8002_dma_resource = open_cfw_gx8002_backup_dma_resource;
    open_cfw_gx8002_dma_irq_handler = open_cfw_gx8002_backup_dma_irq_handler;
    open_cfw_gx8002_request_irq = 0x10004844;
    ''')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    objects=[ROOT/'build/gx8002-backup-dma-deallocate/deallocate.o',ROOT/'build/gx8002-backup-dma-irq/irq.o',ROOT/'build/gx8002-backup-dma-initialize/initialize.o']
    path=out/'combined.elf'
    subprocess.run([pre+'ld','-T',str(script),*[str(p) for p in objects],'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),str(path))
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    sections=[{'name':s['name'],'address':s['address'],'bytes':s['size'],'sha256':sha(e.contents(s))} for s in e.sections if s['flags']&2 and s['size']]
    assert len(sections)==3
    (out/'combined.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'builds':builds,'sections':sections,'source_admitted':False,'limits':['Combined source link only; shifted IRQ entry requires reference and loader qualification.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-dma-combined-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sections'])
