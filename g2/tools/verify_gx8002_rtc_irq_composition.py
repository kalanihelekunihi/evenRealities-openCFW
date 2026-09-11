# SPDX-License-Identifier: MIT
"""RTC init with decoded IRQ registration and controller-enable leaf."""
import json
import subprocess
from itertools import product
from verify_gx8002_rtc_init import build,ROOT,execute,expected,decode
from compare_gx8002_irq import execute as irq_execute


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfc48','--stop-address=0xfc90',str(stock)],text=True))
    new=decode((ROOT/'build/gx8002-board/rtc-init-candidate.disassembly.txt').read_text())
    old_irq=decode(subprocess.check_output([pre,'-D','--start-address=0x174c0','--stop-address=0x17574',str(stock)],text=True))
    new_irq=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-irq/irq.elf')],text=True));count=0
    for outer_source,irq_source,frequency,control in product((False,True),(False,True),(0,32000,65536),(0,0xffffffff)):
        writes=[]
        def hook(number,handler,private):
            leaf=new_irq if irq_source else old_irq
            enable=0x100254ac if irq_source else 0x174c0
            effects=irq_execute(leaf,0x1002553c if irq_source else 0x17550,number,handler,private,enable)
            for effect in effects:
                if effect==('enable',number):writes.extend(irq_execute(leaf,enable,number))
                else:writes.append(effect)
        trace=execute(new if outer_source else old,0x102066bc if outer_source else 0xfc48,frequency,control,irq_hook=hook)
        wanted=[] if frequency>=65536 else [(0x20026f14,0x10206680),(0x20026f18,0),(0xe000e100,16)]
        if trace!=expected(frequency,control) or writes!=wanted:raise ValueError('RTC IRQ composition mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,
            'limits':['Separate RTC/registration/enable frames; other RTC helpers modeled. Existing qualified IRQ artifacts, no hardware interrupt delivery proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-irq-composition.json').write_text(json.dumps(report,indent=2)+'\n');print('RTC IRQ cases:',report['decoded_cases'])
