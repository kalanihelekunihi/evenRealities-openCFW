# SPDX-License-Identifier: MIT
"""Decoded OTP result drives decoded low-power caller selection."""
import json,subprocess
from itertools import product
from verify_gx8002_otp_lowpower_enter import verify as qualify_caller,execute as caller,ROOT,sha
from verify_gx8002_flash_otp_configuration_probe import verify as qualify_otp
from verify_gx8002_flash_otp_configuration import execute as otp
from verify_gx8002_memcpy_source import decode


def verify():
    caller_evidence=qualify_caller();otp_evidence=qualify_otp();directory=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old_caller=decode(subprocess.check_output([pre,'-D','--start-address=0x168e0','--stop-address=0x16954',str(directory/'padmux-get-stock.elf')],text=True))
    old_otp=decode(subprocess.check_output([pre,'-D','--start-address=0x17d18','--stop-address=0x17d88',str(directory/'padmux-get-stock.elf')],text=True))
    new_caller=decode((directory/'otp-lowpower-enter.disassembly.txt').read_text());new_otp=decode((directory/'flash-otp-configuration-candidate.disassembly.txt').read_text());cases=0;sleep_cases=0
    for hz,device,status,content,value in product((0,24576000,0xffffffff),(0,0x20026504),(0,5,0x80000000,0xffffffff),(b'8003A',b'8003B',b'',b'800'),(0,0xffffffff,0x55555555)):
        outcomes=[]
        for outer,outer_entry,inner,inner_entry in ((old_caller,0x168e0,old_otp,0x17d18),(new_caller,0x100248cc,new_otp,0x10025d04)):
            nested=[]
            def hook():
                result,configuration,events=otp(inner,inner_entry,hz,device,status,content,91)
                nested.extend(events)
                return result,configuration
            values={a:value for a in (0xa0000024,0xa0000028,0xa0000038)}
            events=caller(outer,outer_entry,0,0,values,91,otp_hook=hook)
            outcomes.append((nested,events))
        assert outcomes[0]==outcomes[1]
        should_sleep=not(device and not(status&0x80000000) and content==b'8003A')
        assert (('doze',) in outcomes[1][1])==should_sleep
        sleep_cases+=should_sleep;cases+=1
    assert cases==288
    return {'caller':caller_evidence,'otp':otp_evidence,'composed_cases':cases,'sleep_cases':sleep_cases,'source_admitted':False,'limits':['Decoded stock/source OTP policy drives decoded caller; independent sleep-selection assertion includes null probe and read failure. Helper private frames use explicit result/output handoff, not shared stack execution. Flash/clock services remain modeled and hardware unqualified. Caller now fits its slot; admission remains pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-otp-lowpower-configuration.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'],r['sleep_cases'])
