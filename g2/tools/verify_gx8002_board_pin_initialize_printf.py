# SPDX-License-Identifier: MIT
"""Initializer per-entry printf forwarding and continued table processing."""
import json,subprocess
from itertools import product
import verify_gx8002_board_pin_initialize as init
from compare_gx8002_printf_abi import execute as printf
from verify_gx8002_board_pin_initialize_error import verify as data
from verify_gx8002_board_pin_initialize_diagnostic_format import verify as formatting


def verify():
    candidate=init.build();diagnostic=data();formatted=formatting();outers=init.programs()
    pre=str(init.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=init.decode(subprocess.check_output([pre,'-D','--start-address=0x101b0','--stop-address=0x101ce',str(init.ROOT/'build/gx8002-tinyprintf/stock.elf')],text=True))
    new=init.decode(subprocess.check_output([pre,'-d',str(init.ROOT/'build/gx8002-printf/printf.elf')],text=True));count=0
    table=[(p,int(p!=2)) for p in range(13)]
    for outer,wrapper,errors,value in product((0,1),(0,1),(0,8191,*[1<<i for i in range(13)]),(0,37,0xffffffff)):
        calls=[]
        def hook(pointer,pin):
            if pointer!=0x1020ad97:raise ValueError('Initializer diagnostic pointer')
            result,forwarded=printf(new if wrapper else old,0x10206c24 if wrapper else 0x101b0,0x10206a84 if wrapper else 0x10010,[pin],value)
            if forwarded!=[(0,0x1000,[pin])]:raise ValueError('Initializer printf forwarding')
            calls.append(pin);return result
        observed=init.execute(outers[outer],init.ADDRESS if outer else 0xfe2c,table,errors,printf_hook=hook)
        if observed!=init.expected(table,errors,True) or calls!=[p for p in range(13) if errors&(1<<p)]:
            raise ValueError('Initializer diagnostic continuation')
        count+=1
    return {'candidate':candidate,'diagnostic':diagnostic,'formatting':formatted,'combinations':count,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Separate initializer/printf frames and translated format pointer. Formatter/UART verified separately with scripted MMIO. Other initializer helpers modeled; physical hardware unqualified.']}


if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-board-pin-initialize-printf.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer printf combinations:',report['combinations'])
