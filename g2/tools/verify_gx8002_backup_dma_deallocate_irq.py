# SPDX-License-Identifier: MIT
"""Execute linked backup DMA deallocation with its linked PSR leaves."""
import json, subprocess
from itertools import product
from verify_gx8002_backup_dma_deallocate import execute, ROOT, Elf32, sha, decode
from verify_gx8002_uart_receive_irq import irq_execute

def verify():
    path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    elf=Elf32(path.read_bytes(),'cluster')
    standalone=Elf32((ROOT/'build/gx8002-backup-dma-deallocate/deallocate.elf').read_bytes(),'deallocate')
    original=next(s for s in standalone.sections if s['name']=='.text')
    linked=next(s for s in elf.sections if s['name']=='.dma_deallocate')
    assert original['address']==linked['address'] and standalone.contents(original)==elf.contents(linked)
    for name in ('open_cfw_gx8002_backup_dma_deallocate','open_cfw_gx8002_irq_save','open_cfw_gx8002_irq_restore'):
        symbol=next(s for s in elf.symbols() if s['name']==name)
        assert symbol['section'] not in (0,0xfff1)
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([prefix,'-d',str(path)],text=True))
    mapping={0x1000486c:0x10025560,0x10004878:0x1002556c,0x10003be8:0x10025080}
    cases=0
    for flags,channel,token in product(product((0,1,2,255),repeat=2),range(2),(0,0x40,0x140,0x80000000,0xffffffff)):
        psr=[token];transitions=[];gates=[]
        def irq_hook(save,argument):
            result,psr[0]=irq_execute(code,0x1000486c if save else 0x10004878,psr[0],argument)
            transitions.append(psr[0]);return result
        def gate_hook(module,enabled):
            assert psr[0]==token&~0x40
            gates.append((module,enabled))
        trace,memory=execute(code,0x10004bc0,flags,token,channel,irq_hook=irq_hook,gate_hook=gate_hook,helper_addresses=mapping)
        remaining=list(flags);remaining[channel]=0
        assert transitions==[token&~0x40,token] and psr[0]==token
        assert gates==([] if 1 in remaining else [(25,0)])
        assert trace[0]==('irq_save',) and trace[-1]==('irq_restore',token)
        assert memory=={0x2002d3ec:2,**{0x2002d758+i:value for i,value in enumerate(remaining)}}
        cases+=1
    result={'cluster_sha256':sha(path.read_bytes()),'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled deallocator and compiled IRQ leaves execute at their linked addresses with modeled PSR semantics.',
                      'Clock gate is modeled and checked to occur with interrupts disabled; physical interrupt timing and nested machine-stack execution are not qualified.']}
    (ROOT/'docs/research/gx8002-backup-dma-deallocate-irq.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__': print(verify()['decoded_cases'])
