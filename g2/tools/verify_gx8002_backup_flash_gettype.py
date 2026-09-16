# SPDX-License-Identifier: MIT
"""Verify the recovered flash type callback's two pointer reads and return."""
import json, random, subprocess
from build_gx8002_backup_flash_gettype import build, ROOT, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x40898','--stop-address=0x408a4',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-flash-gettype/info.disassembly.txt').read_text())
    rng=random.Random(0x40898);values=[0,1,0xffffffff,0x80000000]+[rng.getrandbits(32) for _ in range(1024)]
    cases=0
    for pointer in (0x20040000,0x20016d6c):
        for value in values:
            memory={};word(memory,0x20016d6c,pointer)
            if pointer!=0x20016d6c:word(memory,pointer,value)
            want=pointer if pointer==0x20016d6c else value
            def forbidden(*args):raise AssertionError('unexpected call')
            for code,entry in ((old,0x40898),(new,0x10007f58)):
                result,after,events=execute(code,entry,[],memory,forbidden)
                assert result[:2]==('return',want) and after==memory and not events
            cases+=1
    report={'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Models readable selected-device memory, including a self-alias. Does not claim invalid pointer safety or discovery ownership.']}
    (ROOT/'docs/research/gx8002-backup-flash-gettype-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
