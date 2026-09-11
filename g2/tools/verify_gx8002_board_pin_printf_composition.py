# SPDX-License-Identifier: MIT
"""Decoded board guard/printf forwarding; formatter is separately verified."""
import json
import subprocess
from itertools import product
from verify_gx8002_board_pin_configure import ROOT, build, programs, execute, expected, decode, ADDRESS
from compare_gx8002_printf_abi import execute as printf
from verify_gx8002_board_pin_error import verify as data
from verify_gx8002_board_pin_diagnostic_format import verify as formatting


def verify():
    candidate=build();diagnostic=data();formatted=formatting();guards=programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x101b0','--stop-address=0x101ce',str(stock)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-printf/printf.elf')],text=True))
    count=0
    for g,w,pin,initialized,check_result,formatter_result in product((0,1),(0,1),
            (0,2,33,0x7fffffff,0x80000000,0xffffffff),(0,1),(0,0xffffffff),(0,37,0xffffffff)):
        seen=[]
        def hook(pointer,argument):
            if (pointer,argument)!=(0x1020ad4a,pin):raise ValueError('Board printf boundary')
            result,calls=printf(new if w else old,0x10206c24 if w else 0x101b0,
                                0x10206a84 if w else 0x10010,[argument],formatter_result)
            if calls!=[(0,0x1000,[pin])]:raise ValueError('Board printf forwarding')
            seen.append(argument)
            return result
        result=execute(guards[g],ADDRESS if g else 0xfd68,pin,3,initialized,check_result,0,0,printf_hook=hook)
        if result!=expected(pin,3,initialized,check_result):raise ValueError('Board printf guard result')
        if seen!=([pin] if initialized==0 and check_result else []):raise ValueError('Board printf call count')
        count+=1
    return {'candidate':candidate,'diagnostic':diagnostic,'formatting':formatted,
            'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Separate checked guard/wrapper frames; pointer translated to harness address. Formatter independently verified; formatter/integer/padding/putf composition verified separately; fputc return and physical UART remain modeled.']}


if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-board-pin-printf-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board pin printf cases:',report['decoded_cases'])
