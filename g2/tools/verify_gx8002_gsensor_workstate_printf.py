# SPDX-License-Identifier: MIT
"""Decoded gsensor accessor/printf wrapper call-boundary composition."""
import json,subprocess
from itertools import product
import verify_gx8002_gsensor_workstate as state
from compare_gx8002_printf_abi import execute as printf
from verify_gx8002_gsensor_workstate_message import verify as data
from verify_gx8002_gsensor_workstate_format import verify as formatting


def verify():
    candidate=state.build();message=data();formatted=formatting();outers=state.programs()
    pre=str(state.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=state.decode(subprocess.check_output([pre,'-D','--start-address=0x101b0','--stop-address=0x101ce',str(state.ROOT/'build/gx8002-tinyprintf/stock.elf')],text=True))
    new=state.decode(subprocess.check_output([pre,'-d',str(state.ROOT/'build/gx8002-printf/printf.elf')],text=True));count=0
    for outer,wrapper,before,after,value in product((0,1),(0,1),(0,1,0x80000000,0xffffffff),(0,2,0xffffffff),(0,37,0xffffffff)):
        calls=[]
        def hook(pointer,argument):
            if (pointer,argument)!=(0x1020adaa,before):raise ValueError('State diagnostic boundary')
            result,forwarded=printf(new if wrapper else old,0x10206c24 if wrapper else 0x101b0,0x10206a84 if wrapper else 0x10010,[argument],value)
            if forwarded!=[(0,0x1000,[before])]:raise ValueError('State printf forwarding')
            calls.append(argument);return result
        observed=state.execute(outers[outer],state.ADDRESS if outer else 0xfe94,before,after,0,printf_hook=hook)
        if observed!=state.expected(before,after) or calls!=[before]:raise ValueError('State printf composition')
        count+=1
    return {'candidate':candidate,'message':message,'formatting':formatted,'combinations':count,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Separate accessor/printf frames and translated format pointer. Formatter/UART checked separately with scripted MMIO; before/after state values modeled, lifecycle unqualified.']}


if __name__=='__main__':
    report=verify();(state.ROOT/'docs/research/gx8002-gsensor-workstate-printf.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Gsensor printf combinations:',report['combinations'])
