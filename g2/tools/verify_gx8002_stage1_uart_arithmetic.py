# SPDX-License-Identifier: MIT
"""Execute linked UART and arithmetic in one register frame against stock."""
import json
import subprocess
from itertools import product
from build_gx8002_stage1_initialize import build
from build_gx8002_backup_cfft import ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_stage1_uart_configure import execute, MASK
from verify_gx8002_uart_stage1_divmod import oracle


def verify():
    evidence=build()
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old={}
    for start,end in ((0x39774,0x397f4),(0x39bb4,0x39c34)):
        old.update(decode(subprocess.check_output([tool,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True)))
    new=decode((ROOT/'build/gx8002-stage1-initialize/initialize.disassembly.txt').read_text())
    helpers={0x38c54:'frequency',0x39774:'divide',0x397b8:'remainder'}
    mapped={a-0x38954+0x10000000:n for a,n in helpers.items()}
    cases=0
    for baud,retain,frequency,busy in product((0,1,9600,115200,0x0fffffff,0x10000000,MASK),(0,1,MASK),(0,1,32768,24000000,0x80000000,MASK),((0,0),(1,3),(4,2))):
        a=execute(old,0x39bb4,helpers,baud,retain,frequency,busy,True)
        b=execute(new,0x10001260,mapped,baud,retain,frequency,busy,True)
        assert a==b,(baud,retain,frequency,busy)
        expected=[[0xa0100004,0],[0xa0100010,3]]
        if not retain:
            den=(baud<<4)&MASK
            divisor=oracle(frequency,den,False);rem=oracle(frequency,den,True)
            fraction=oracle((oracle((rem*100)&MASK,den,False)<<4)&MASK,100,False)
            expected += [[0xa010000c,128],[0xa0100000,divisor&255],[0xa0100004,(divisor>>8)&255],[0xa01000c0,fraction&255]]
        expected += [[0xa010000c,3],[0xa0100008,79]]
        assert [e[1:] for e in b if e[0]=='write']==expected
        cases+=1
    report={'cases':cases,'build':evidence,'limits':['Actual stock/source UART and arithmetic instructions execute in one register frame; ordered traces, independent write oracle and ABI checked.', 'Frequency response and finite MMIO busy sequences remain modeled. Physical hardware and firmware integration unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-uart-arithmetic-execution.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    print(verify()['cases'],'composed UART/arithmetic cases passed')
