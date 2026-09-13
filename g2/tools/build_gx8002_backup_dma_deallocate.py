# SPDX-License-Identifier: MIT
"""Build backup-specific two-channel deallocator on macOS; candidate only."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-dma-deallocate';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_dma_deallocate.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'deallocate.o')],check=True)
    rt=lambda p:p-0x3b940+0x10003000
    bindings={'open_cfw_gx8002_backup_dma_state':0x2002d3e8,'open_cfw_gx8002_backup_irq_save':rt(0x3d1ac),'open_cfw_gx8002_backup_irq_restore':rt(0x3d1b8),'open_cfw_gx8002_backup_dma_resource':rt(0x3c528)}
    script=out/'deallocate.ld'
    script.write_text('SECTIONS { .text %#x : { *(.text*) } }\n'%rt(0x3d500)+''.join('%s = %#x;\n'%(k,v) for k,v in bindings.items()))
    subprocess.run([pre+'ld','-T',str(script),str(out/'deallocate.o'),'-o',str(out/'deallocate.elf')],check=True)
    e=Elf32((out/'deallocate.elf').read_bytes(),'candidate');s=next(s for s in e.sections if s['name']=='.text');body=e.contents(s)
    assert not e.relocations(s['index']) and not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'deallocate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'deallocate.elf')],text=True))
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(body),'compiled_sha256':sha(body),'envelope_bytes':68,'fits':len(body)<=68,'bindings':bindings,'source_admitted':False,'limits':['Candidate only; decoded equivalence and placement pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-dma-deallocate-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
