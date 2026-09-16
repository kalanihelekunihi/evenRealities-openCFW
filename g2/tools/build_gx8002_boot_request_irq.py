# SPDX-License-Identifier: MIT
"""Reuse recovered IRQ-registration C for the earlier boot image."""
import json
import subprocess
from itertools import product
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32, FLAGS
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_request_irq import execute


def build():
    out=ROOT/'build/gx8002-boot-request-irq';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_request_irq.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*FLAGS,'-Os','-c',str(source),'-o',str(out/'request.o')]
    subprocess.run(command,check=True)
    ld=out/'request.ld'
    ld.write_text('SECTIONS { .text 0x100030e8 : { *(.text*) } }\nopen_cfw_gx8002_backup_irq_table = 0x2000984c;\nASSERT(SIZEOF(.text) <= 40, "boot registration overflow")\n')
    path=out/'request.elf';subprocess.run([pre+'ld','-T',str(ld),str(out/'request.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'boot registration');sec=next(s for s in elf.sections if s['name']=='.text')
    assert {s['name'] for s in elf.sections if s['flags']&2}=={'.text'}
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oldelf=Elf32(wrapper.read_bytes(),'stock')
    assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3138','--stop-address=0x3158',str(wrapper)],text=True))
    backup=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3d184','--stop-address=0x3d1a4',str(wrapper)],text=True))
    disassembly=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'request.disassembly.txt').write_text(disassembly);new=decode(disassembly)
    cases=0
    for irq,handler,context in product((*range(34),0x80000000,0xffffffff),(0,0x10004454,0xffffffff),(0,0x12345678,0xffffffff)):
        expected=[] if irq>=32 or not handler else [(0x2000984c+irq*8,handler),(0x20009850+irq*8,context),(0xe000e100,1<<irq)]
        a=execute(old,0x3138,irq,handler,context);b=execute(new,0x100030e8,irq,handler,context)
        assert a==b==expected
        other=execute(backup,0x3d184,irq,handler,context)
        if expected:
            assert other==[(0x200173a8+irq*8,handler),(0x200173ac+irq*8,context),expected[-1]]
            assert not {x[0] for x in a[:-1]} & {x[0] for x in other[:-1]}
        else:assert not other
        cases+=1
    return {'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_sha256':IMAGE_SHA,'code_bytes':sec['size'],'stock_envelope_bytes':40,'cases':cases,'boot_table':0x2000984c,'backup_table':0x200173a8,'source_admitted':False,'limits':['Complete shared C linked at earlier-image mapping candidate and exact ordered stores checked against stock. Table writes are disjoint; hardware enable register shared. This alone does not prove image transition, vector replacement or interrupt lifetime. Not integrated.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-boot-request-irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['code_bytes'],'source bytes;',result['cases'],'registration/table-separation cases')
