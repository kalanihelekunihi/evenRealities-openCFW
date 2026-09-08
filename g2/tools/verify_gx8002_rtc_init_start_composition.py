#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded RTC init/start call boundary and resulting control register writes."""
import json,subprocess
from itertools import product
import verify_gx8002_rtc_init as init
import verify_gx8002_rtc_ticks as ticks
from verify_gx8002_padmux_get import build as build_getter,programs


def verify():
    candidate=init.build();start=ticks.start();build_getter();programs()
    out=init.ROOT/'build/gx8002-board';pre=str(init.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def stock(first,last):
        return init.decode(subprocess.check_output([pre,'-D',f'--start-address={first:#x}',f'--stop-address={last:#x}',str(out/'padmux-get-stock.elf')],text=True))
    old=stock(0xfc48,0xfc90);old_start=stock(0xfc2c,0xfc3c)
    new=init.decode((out/'rtc-init-candidate.disassembly.txt').read_text())
    new_start=init.decode((out/'rtc-start-tick-candidate.disassembly.txt').read_text())
    count=calls=0
    for outer,leaf,frequency,control in product((0,1),(0,1),(0,32768,65535,65536,0xffffffff),(0,0xffffffff,0x12345678)):
        reads=[]
        def hook():
            nonlocal calls
            trace=ticks.execute(new_start if leaf else old_start,0x102066a0 if leaf else 0xfc2c,control|16,'start')
            if trace!=ticks.expected(control|16,'start'):raise ValueError('RTC composed start mismatch')
            reads.extend(trace);calls+=1
        trace=init.execute(new if outer else old,init.ADDRESS if outer else 0xfc48,frequency,control,start_hook=hook)
        if trace!=init.expected(frequency,control):raise ValueError('RTC composed init mismatch')
        wanted=[] if frequency>=65536 else [('read',0xa000300c,control|16),('write',0xa000300c,control|20)]
        if reads!=wanted:raise ValueError('RTC composed control state mismatch')
        count+=1
    return {'candidate':candidate,'start_candidate':start,'combinations':count,'start_calls':calls,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded init/start call boundaries; clock/frequency/IRQ/printf still modeled without control-register mutation between init write and start read. Separate helper stacks. No hardware or concurrency proof.']}

if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-rtc-init-start-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RTC init/start combinations:',report['combinations'])
