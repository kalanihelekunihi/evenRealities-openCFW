# SPDX-License-Identifier: MIT
"""Build backup DMA initialization on macOS; candidate only."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-dma-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_dma_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'initialize.o')],check=True)
    rt=lambda p:p-0x3b940+0x10003000
    bindings={'open_cfw_gx8002_dma_state':0x2002d3e8,'open_cfw_gx8002_dma_irq_handler':rt(0x3d544),'open_cfw_gx8002_dma_resource':rt(0x3c528),'open_cfw_gx8002_request_irq':rt(0x3d184)}
    script=out/'initialize.ld'
    script.write_text('SECTIONS { .text %#x : { *(.text*) } }\n'%rt(0x3d654)+''.join('%s = %#x;\n'%(k,v) for k,v in bindings.items()))
    subprocess.run([pre+'ld','-T',str(script),str(out/'initialize.o'),'-o',str(out/'initialize.elf')],check=True)
    e=Elf32((out/'initialize.elf').read_bytes(),'candidate');s=next(s for s in e.sections if s['name']=='.text');body=e.contents(s)
    assert not e.relocations(s['index']) and not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'initialize.elf')],text=True))
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(body),'compiled_sha256':sha(body),'envelope_bytes':128,'fits':len(body)<=128,'bindings':bindings,'source_admitted':False,'limits':['Candidate only; decoded equivalence and placement pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-dma-initialize-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
