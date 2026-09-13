# SPDX-License-Identifier: MIT
"""OTP policy calls decoded source flash initializer with real input registers."""
import json,subprocess
from itertools import product
from verify_gx8002_flash_otp_configuration_literals import verify as qualify
from verify_gx8002_flash_otp_configuration import execute,ROOT,sha
from verify_gx8002_flash_probe_callback_owner import verify as owners
from execute_gx8002_otp_interface import execute as interface
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=qualify();ownership=owners();directory=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16450','--stop-address=0x16604',str(directory/'padmux-get-stock.elf')],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(directory/'flash-interface.elf')],text=True))
    outer=decode((directory/'flash-otp-configuration-candidate.disassembly.txt').read_text());cases=0;calls=0
    for hz,failure,chip,status,content in product((0,1,24576000,0xffffffff),(0,1,0xffffffff),(0x854012,0xc22017,0x204016,0x1c3812,0x684015,0xffffffff),(0,64,255),(b'8003A',b'8003B')):
        device=0 if failure else 0x20026504
        def probe(target,args):
            nonlocal calls
            assert target==ownership['callback_target'] and args==(0,0,hz>>1,2048)
            a=interface(old,0x16450,0x1000dfec,91,0,failure,chip,status,args)
            b=interface(new,target,0,91,0,failure,chip,status,args)
            assert a==b and b['result']==device
            calls+=1
            return b['result']
        actual=execute(outer,0x10025d04,hz,device,5,content,91,probe_hook=probe)
        expected=execute(outer,0x10025d04,hz,device,5,content,91)
        assert actual==expected
        cases+=1
    assert cases==432 and calls==432
    return {'evidence':evidence,'ownership':ownership,'probe_cases':cases,'decoded_interface_calls':calls,'executor_sha256':sha((ROOT/'tools/execute_gx8002_otp_interface.py').read_bytes()),'source_admitted':False,'limits':['Actual four caller argument registers supplied to decoded stock and source initializer; initializer return drives OTP policy. Nested initialization uses private frames and scripted peripheral helpers; physical flash and enclosing caller still unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-otp-configuration-probe.json').write_text(json.dumps(r,indent=2)+'\n');print(r['probe_cases'])
