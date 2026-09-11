# SPDX-License-Identifier: MIT
"""Fatal setup printf forwarding precedes the decoded terminal self-branch."""
import json,subprocess
from itertools import product
import verify_gx8002_board_pin_setup as setup
from compare_gx8002_printf_abi import execute as printf
from verify_gx8002_board_pin_setup_error import verify as data
from verify_gx8002_board_pin_setup_diagnostic_format import verify as formatting


def verify():
    candidate=setup.build();diagnostic=data();formatted=formatting();outers=setup.programs()
    pre=str(setup.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=setup.decode(subprocess.check_output([pre,'-D','--start-address=0x101b0','--stop-address=0x101ce',str(setup.ROOT/'build/gx8002-tinyprintf/stock.elf')],text=True))
    new=setup.decode(subprocess.check_output([pre,'-d',str(setup.ROOT/'build/gx8002-printf/printf.elf')],text=True));count=0
    for outer,wrapper,failed,value in product((0,1),(0,1),(False,True),(0,48,0xffffffff)):
        calls=[]
        def hook(pointer):
            if pointer!=0x1020ad66:raise ValueError('Setup fatal diagnostic pointer')
            result,forwarded=printf(new if wrapper else old,0x10206c24 if wrapper else 0x101b0,0x10206a84 if wrapper else 0x10010,[],value)
            if forwarded!=[(0,0x1000,[])]:raise ValueError('Setup printf forwarding')
            calls.append(pointer);return result
        results=[setup.MASK if failed else 0]+[0]*7
        observed=setup.execute(outers[outer],setup.ADDRESS if outer else 0xfda8,results,printf_hook=hook)
        if observed!=setup.expected(results) or calls!=([0x1020ad66] if failed else []):raise ValueError('Setup printf terminal path')
        count+=1
    return {'candidate':candidate,'diagnostic':diagnostic,'formatting':formatted,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Separate setup/printf frames and translated format pointer; Formatter/output bodies checked separately with scripted UART MMIO. Original fatal loop reached after printf returns.']}


if __name__=='__main__':
    report=verify();(setup.ROOT/'docs/research/gx8002-board-pin-setup-printf.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Setup printf combinations:',report['combinations'])
