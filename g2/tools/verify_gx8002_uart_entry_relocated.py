# SPDX-License-Identifier: MIT
import json
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_irq_software_frame import execute


def verify():
    candidate=build();path=ROOT/'build/gx8002-uart-configure-source/uart.elf';elf=Elf32(path.read_bytes(),str(path))
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'uart.disassembly.txt').read_text());cases=0
    for seed in (0,1,0xffffffff,0x55555555,0xaaaaaaaa,0x80000000):
        for depth in range(4):
            for architecture in (False,True):
                result=execute(code,symbols['open_cfw_gx8002_irq_entry'],seed,depth,architecture=architecture,body_target=symbols['open_cfw_gx8002_irq_dispatch_body'])
                expected={'calls':1,'software_frame_bytes':100,'modeled_peak_bytes':(136 if architecture else 104)*(depth+1)}
                if result!=expected:raise ValueError(('Relocated IRQ frame',result,expected))
                cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Relocated wrapper instructions execute; body effects modeled as register clobbers and callback stack. Hardware frames use an existing architectural model, not physical CPU execution. Actual dispatch/handler stack demand and hardware nesting remain separate.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-entry-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated entry cases:',r['cases'])
