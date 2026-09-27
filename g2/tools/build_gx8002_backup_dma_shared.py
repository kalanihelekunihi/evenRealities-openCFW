# SPDX-License-Identifier: MIT
"""Build recovered DMA C together to share pools and preserve both entry points."""
import json,subprocess
from build_gx8002_backup_dma_deallocate import ROOT,FLAGS,Elf32,sha

def build():
    out=ROOT/'build/gx8002-backup-dma-shared-pool';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002'
    paths=[src/'runtime_gx8002_backup_dma_deallocate.c',src/'runtime_gx8002_backup_dma_irq_handler.c',src/'runtime_gx8002_backup_dma_pool.c']
    text=paths[0].read_text()+'\n'+paths[1].read_text().replace('open_cfw_gx8002_backup_dma_state','open_cfw_gx8002_backup_dma_state_words')+'\n'+paths[2].read_text()
    (out/'pair.c').write_text(text);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-fno-function-sections','--param=max-completely-peel-times=0']
    subprocess.run([pre+'gcc',*flags,'-c',str(out/'pair.c'),'-o',str(out/'pair.o')],check=True)
    bindings={'open_cfw_gx8002_backup_dma_state':0x2002d3e8,'open_cfw_gx8002_backup_dma_state_words':0x2002d3e8,'open_cfw_gx8002_backup_dma_callbacks':0x200174a8,'open_cfw_gx8002_backup_irq_save':0x1000486c,'open_cfw_gx8002_backup_irq_restore':0x10004878,'open_cfw_gx8002_backup_dma_resource':0x10003be8}
    (out/'pair.ld').write_text('SECTIONS { .text 0x10004bc0 : { *(.text*) } .callback_pointer 0x10004c78 : { *(.backup_callback_pointer) } ASSERT(. <= 0x10004c7c, "DMA overflow") }\n'+''.join('%s = %#x;\n'%(k,v) for k,v in bindings.items()))
    subprocess.run([pre+'ld','-T',str(out/'pair.ld'),str(out/'pair.o'),'-o',str(out/'pair.elf')],check=True)
    e=Elf32((out/'pair.elf').read_bytes(),'pair');allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==2
    section=next(s for s in allocated if s['name']=='.text')
    pointer=next(s for s in allocated if s['name']=='.callback_pointer')
    assert section['size']==180 and pointer['address']==0x10004c78 and pointer['size']==4
    assert e.contents(pointer)==(0x200174a8).to_bytes(4,'little')
    symbols={s['name']:s['value'] for s in e.symbols()}
    assert symbols['open_cfw_gx8002_backup_dma_deallocate']==0x10004bc0
    assert symbols['open_cfw_gx8002_backup_dma_irq_handler']==0x10004c00
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    (out/'pair.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'pair.elf')],text=True))
    return {'source_sha256':{p.name:sha(p.read_bytes()) for p in paths},'generated_source_sha256':sha(text.encode()),'flags':flags,'bindings':bindings,'pointer_bytes':pointer['size'],'pointer_sha256':sha(e.contents(pointer)),'compiled_bytes':section['size'],'compiled_sha256':sha(e.contents(section)),'source_admitted':False,'limits':['Shared source compilation preserves entries; behavior, tail and loader admission separate.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-dma-shared-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],'bytes')
