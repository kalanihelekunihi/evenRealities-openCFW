# SPDX-License-Identifier: MIT
"""Decoded flash type API callback forwarding and missing-slot return."""
import json,subprocess
from itertools import product
from build_gx8002_backup_flash_type import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute


def verify():
    candidate=build();assert candidate['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x4094c','--stop-address=0x40958',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-flash-type/flash-type-api-candidate.disassembly.txt').read_text());cases=0
    for target,address,length,result in product((0,0x10023788,0x10212340),(0,1,0xffffffff),(0,1,256,0xffffffff),(0,1,0xffffffff,0x80000000)):
        memory={};word(memory,0x20031030,target);args=[0x20031000,address,0x20040000,length]
        for code,entry in ((old,0x4094c),(new,0x1000800c)):
            calls=[]
            def callback(destination,parameters,state,events):
                assert destination==target and target
                calls.append(True);return result
            outcome,after,events=execute(code,entry,args,memory,callback)
            assert outcome[:2]==('return',result if target else 0) and after==memory and not events
            assert len(calls)==int(bool(target))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded callback forwarding/return and ABI checked; buffer IO and callback implementation modeled. Caller/dependency integration pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-flash-type-api-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
