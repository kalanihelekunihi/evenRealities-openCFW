# SPDX-License-Identifier: MIT
"""Decoded digital LDO query against stock and independent bit truth table."""
import json, random, subprocess
from build_gx8002_digital_control_candidate import build, ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word


def verify():
    candidate=build();assert candidate['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16724','--stop-address=0x16744',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-board/digital-control-candidate.disassembly.txt').read_text())
    rng=random.Random(0x16724);values=list(range(256))+[0xffffffff,0xfffffffe,0x80000000]+[rng.getrandbits(32) for _ in range(4096)]
    for value in values:
        memory={};word(memory,0xa0005058,value)
        want=(0,0,1,2)[(value>>1)&3]
        for code,entry in ((old,0x16724),(new,0x10024710)):
            def forbidden(*args):raise AssertionError('Unexpected helper call')
            result,after,events=execute(code,entry,[],memory,forbidden)
            assert result[:2]==('return',want) and after==memory and not events
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded leaf and independent four-state truth table; private read-only MMIO input. System caller integration pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-digital-control-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['cases'])
