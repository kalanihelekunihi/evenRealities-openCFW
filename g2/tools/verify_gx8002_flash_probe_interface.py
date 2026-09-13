# SPDX-License-Identifier: MIT
"""Probe wrapper invokes the authenticated decoded flash-interface initializer."""
import json,subprocess
from verify_gx8002_flash_probe_callback_owner import verify as owners
from verify_gx8002_flash_probe_timer import verify as qualify
from verify_gx8002_flash_probe import oracle
from execute_gx8002_flash_probe import execute
from compare_gx8002_flash_interface_full import execute as interface
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def verify():
    ownership=owners();evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(IMAGE.read_bytes())==IMAGE_SHA and sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16450','--stop-address=0x16604',str(path)],text=True));new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/flash-interface.elf')],text=True));probe=decode((ROOT/'build/gx8002-board/flash-probe-candidate.disassembly.txt').read_text());calls=[];cases=0
    for chip in (0x854012,0xc22017,0x204016,0x1c3812,0x684015,0xffffffff):
        for status in (0,64,255):
            for returned in ((0x20026504,),(0,0x20026504),(0,0)):
                def callback(target,args,wanted):
                    assert target==ownership['callback_target'] and args==(0,0,8000000,0)
                    failure=0 if wanted else 1
                    a=interface(old,0x16450,0x1000dfec,0xffffffff,0,failure,chip,status)
                    b=interface(new,target,0,0xffffffff,0,failure,chip,status)
                    assert a==b and b['result']==wanted and b['frame_bytes']==48
                    calls.append(b['trace']);return b['result']
                args=(0,0,8000000,0);states=(0,0);times=(0,4999999,5000000);pointers=(ownership['callback_target'],)*2
                result=execute(probe,0x1002475c,args,states,times,returned,pointers,probe_runner=callback)
                assert result==oracle(args,states,times,returned,pointers);cases+=1
    assert cases==54 and len(calls)==90
    return {'evidence':evidence,'ownership':ownership,'probe_cases':cases,'decoded_interface_calls':len(calls),'source_admitted':False,
            'limits':['Decoded callback result drives actual probe retry and success state write; callback MMIO trace stock/source compared.',
                       'Callback uses private frames and modeled peripheral services; callback state is not shared between attempts. Physical flash operation unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-probe-interface.json').write_text(json.dumps(r,indent=2)+'\n');print(r['probe_cases'],r['decoded_interface_calls'])
