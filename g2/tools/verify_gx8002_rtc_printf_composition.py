# SPDX-License-Identifier: MIT
"""RTC diagnostic call through decoded printf wrapper and verified formatting."""
import json
import subprocess
from itertools import product
from verify_gx8002_rtc_init import build,ROOT,execute,expected,decode
from compare_gx8002_printf_abi import execute as printf
from verify_gx8002_rtc_diagnostic_format import verify as formatting


def verify():
    candidate=build();formatted=formatting();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfc48','--stop-address=0xfc90',str(stock)],text=True))
    new=decode((ROOT/'build/gx8002-board/rtc-init-candidate.disassembly.txt').read_text())
    old_printf=decode(subprocess.check_output([pre,'-D','--start-address=0x101b0','--stop-address=0x101ce',str(stock)],text=True))
    new_printf=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-printf/printf.elf')],text=True));count=0
    for outer_source,wrapper_source,frequency,control in product((False,True),(False,True),(32000,65536,0xffffffff),(0,0xffffffff)):
        emitted=[]
        def hook(pointer):
            if pointer!=0x1020ad04:raise ValueError('RTC diagnostic pointer')
            result,calls=printf(new_printf if wrapper_source else old_printf,0x10206c24 if wrapper_source else 0x101b0,
                                0x10206a84 if wrapper_source else 0x10010,[],formatted['formatter_result'])
            if calls!=[(0,0x1000,[])]:raise ValueError('RTC printf forwarding')
            emitted.append(formatted['output_text']);return result
        trace=execute(new if outer_source else old,0x102066bc if outer_source else 0xfc48,frequency,control,printf_hook=hook)
        if trace!=expected(frequency,control) or emitted!=([formatted['output_text']] if frequency>=65536 else []):
            raise ValueError('RTC printf composition mismatch')
        count+=1
    return {'candidate':candidate,'formatting':formatted,'decoded_cases':count,'source_admitted':False,
            'limits':['Separate frames and diagnostic pointer translated to formatter harness address; formatter output composed from verified no-argument string. Physical UART remains modeled.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-printf-composition.json').write_text(json.dumps(report,indent=2)+'\n');print('RTC printf cases:',report['decoded_cases'])
