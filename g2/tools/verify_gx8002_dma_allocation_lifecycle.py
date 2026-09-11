# SPDX-License-Identifier: MIT
"""Persist allocation bytes across decoded select/free calls."""
import json,subprocess
from itertools import product
from verify_gx8002_dma_select import verify as select_verify,execute as select,ROOT,decode
from verify_gx8002_dma_deallocate import verify as free_verify,execute as free

def verify():
    selection=select_verify();deallocation=free_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcfd8','--stop-address=0xd068',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new_select=decode((ROOT/'build/gx8002-dma-select/select.disassembly.txt').read_text());new_free=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=calls=0
    for selection_source,free_source,initial,actions in product((False,True),(False,True),product((0,1,2,255),repeat=2),product(('select','free0','free1'),repeat=4)):
        allocation=list(initial);wanted=list(initial)
        for index,action in enumerate(actions):
            token=(0,0x40,0xffffffff,0x80000040)[index]
            if action=='select':
                result,trace,memory=select(new_select if selection_source else old,0x10203a4c if selection_source else 0xcfd8,allocation,token)
                expected=next((i for i,v in enumerate(wanted) if v==0),0xffffffff)
                gate=[]
                if expected!=0xffffffff:wanted[expected]=1;gate=[('resource',25,1)]
                if result!=expected:raise ValueError('Lifecycle selection result')
            else:
                channel=int(action[-1]);trace,memory=free(new_free if free_source else old,0x10203a98 if free_source else 0xd024,allocation,token,channel)
                wanted[channel]=0;gate=[] if 1 in wanted else [('resource',25,0)]
            allocation=[memory[0x2002ecac+i] for i in range(2)]
            if allocation!=wanted:raise ValueError('Lifecycle persisted state')
            if [x for x in trace if x[0]=='resource']!=gate:raise ValueError('Lifecycle clock calls')
            if trace[0]!=('irq_save',) or trace[-1]!=('irq_restore',token):raise ValueError('Lifecycle critical section')
            calls+=1
        cases+=1
    return {'selection_dependency':selection,'deallocation_dependency':deallocation,'sequences':cases,'decoded_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Persistent allocation-byte state across four operations; per-call registers/frames recreated. IRQ and clock helpers modeled; no interrupt interleavings or real DMA ownership proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-allocation-lifecycle.json').write_text(json.dumps(report,indent=2)+'\n');print('Allocation lifecycle:',report['sequences'],report['decoded_calls'])
