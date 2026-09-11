# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_transmit_dma import verify as dma_verify,execute as dma_execute,ROOT,decode
from verify_gx8002_dma_select import verify as select_verify,execute as select_execute,expected

def verify():
    dma=dma_verify();selection=select_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc694','--stop-address=0xd024',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-dma/dma.disassembly.txt').read_text());new_select=decode((ROOT/'build/gx8002-dma-select/select.disassembly.txt').read_text());cases=0
    for outer,leaf,port,allocation,token in product((False,True),(False,True),(0,1),([0,0],[1,0],[0,255],[1,128]),(0,0x40,0xffffffff)):
        seen=[]
        def hook():
            result=select_execute(new_select if leaf else old,0x10203a4c if leaf else 0xcfd8,allocation,token)
            if result!=expected(allocation,token):raise ValueError('Transmit allocator effects')
            seen.append(result);return result[0]
        result=dma_execute(new if outer else old,0x10203108 if outer else 0xc694,port,0x20050000,80,0,3,4,0xffffffff,select_hook=hook)
        channel=expected(allocation,token)[0]
        if len(seen)!=1 or result[0]!=(0xffffffff if channel==0xffffffff else 0):raise ValueError('Transmit allocator result')
        writes=[e for e in result[1] if e[0]=='write' and e[1]==0x20026b10]
        if writes!=([] if channel==0xffffffff else [('write',0x20026b10,channel)]):raise ValueError('Transmit allocated channel storage')
        transfers=[x for x in result[1] if x[0]=='transfer']
        wanted=[] if channel==0xffffffff else [('transfer',0xa0000000,0x20050000,80,channel,(0,3,0,0,0,0,4,1,7 if port==0 else 5,1,0,1))]
        if transfers!=wanted:raise ValueError('Allocated channel transfer handoff')
        callbacks=[x for x in result[1] if x[0]=='callback']
        if callbacks!=([] if channel==0xffffffff else [('callback',channel,0x102030c4,0x20026a94)]):raise ValueError('Allocated channel callback handoff')
        cases+=1
    return {'dma_dependency':dma,'selection_dependency':selection,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate allocator state and frame; IRQ/clock helpers modeled. Valid ports only; invalid-port repair is qualified separately.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-select.json').write_text(json.dumps(report,indent=2)+'\n');print('Transmit allocator cases:',report['decoded_cases'])
