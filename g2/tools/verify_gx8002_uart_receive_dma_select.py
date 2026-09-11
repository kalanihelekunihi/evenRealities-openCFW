# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_dma import verify as dma_verify,execute as dma_execute,ROOT,decode
from verify_gx8002_dma_select import verify as select_verify,execute as select_execute,expected

def verify():
    dma=dma_verify();selection=select_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc71c','--stop-address=0xd024',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-dma/dma.disassembly.txt').read_text());new_select=decode((ROOT/'build/gx8002-dma-select/select.disassembly.txt').read_text());cases=0
    for outer,leaf,port,allocation,token in product((False,True),(False,True),(0,1,2),([0,0],[1,0],[0,255],[1,128]),(0,0x40,0xffffffff)):
        seen=[]
        def hook():
            result=select_execute(new_select if leaf else old,0x10203a4c if leaf else 0xcfd8,allocation,token)
            if result!=expected(allocation,token):raise ValueError('Receive allocator effects')
            seen.append(result);return result[0]
        result=dma_execute(new if outer else old,0x10203190 if outer else 0xc71c,port,0x20050000,80,0,3,4,0xffffffff,select_hook=hook)
        channel=expected(allocation,token)[0]
        if len(seen)!=1 or result[0]!=(0xffffffff if channel==0xffffffff or port==2 else 0):raise ValueError('Receive allocator result')
        writes=[e for e in result[1] if e[0]=='write' and e[1]==0x20026afc]
        if writes!=([] if channel==0xffffffff else [('write',0x20026afc,channel)]):raise ValueError('Receive allocated channel storage')
        cases+=1
    return {'dma_dependency':dma,'selection_dependency':selection,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate allocator state and frame; IRQ/clock helpers modeled. Invalid port is checked after channel reservation, matching stock without adding cleanup.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-receive-dma-select.json').write_text(json.dumps(report,indent=2)+'\n');print('Receive allocator cases:',report['decoded_cases'])
