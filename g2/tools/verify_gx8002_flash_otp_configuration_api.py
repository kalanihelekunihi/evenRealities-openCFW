# SPDX-License-Identifier: MIT
"""OTP configuration executes reconstructed read API against shared local RAM."""
import json,subprocess
from itertools import product
from verify_gx8002_flash_otp_configuration import verify as qualify,execute,ROOT,sha,MASK
from execute_gx8002_clock_source_select import execute as dispatch
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32


def verify():
    evidence=qualify();directory=ROOT/'build/gx8002-board'
    path=directory/'flash-otp-read-api-candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    reviewed=json.loads((ROOT/'docs/research/gx8002-flash-otp-read-api-source-verification.json').read_text())
    for row in reviewed['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    code=decode((directory/'flash-otp-configuration-candidate.disassembly.txt').read_text())
    cases=0;calls=0
    for target,status,content in product((0,0x10023fa4),(0,5,0x80000000,MASK),(b'',b'800',b'8003A',b'8003B',b'\0'*5)):
        def read_hook(args,memory):
            nonlocal calls
            device,offset,buffer,length=args
            word(memory,device+88,target)
            def callback(destination,parameters,state,events):
                nonlocal calls
                assert destination==target and parameters[:3]==[offset,buffer,length]
                assert bytes(state[buffer+i] for i in range(5))==bytes(5)
                for i,value in enumerate(content):state[buffer+i]=value
                calls+=1
                return status
            outcome,after,events=dispatch(wrapper,0x100247f4,list(args),memory,callback)
            assert outcome[0]=='return' and not events
            memory.update(after)
            return outcome[1]
        actual=execute(code,0x10025d04,24576000,0x20026504,0,b'',91,read_hook=read_hook)
        result=status if target else MASK
        expected=execute(code,0x10025d04,24576000,0x20026504,result,content if target else b'',91)
        assert actual==expected
        cases+=1
    assert cases==40 and calls==20
    return {'evidence':evidence,'api_cases':cases,'decoded_api_callbacks':calls,'api_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual decoded API dispatch shares caller local memory; missing callback, partial writes and signed status tested. SPI callback effects remain scripted; no hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-otp-configuration-api.json').write_text(json.dumps(r,indent=2)+'\n');print(r['api_cases'])
