# SPDX-License-Identifier: MIT
"""Decoded raw hardware-counter conversion feeding the flash probe timeout."""
import json,subprocess
from verify_gx8002_flash_probe import verify as qualify,oracle,ROOT
from execute_gx8002_flash_probe import execute
from verify_gx8002_clock_time_us_candidate import execute as timer
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-board/clock-time-us-candidate.elf';elf=Elf32(path.read_bytes(),'timer');report=json.loads((ROOT/'docs/research/gx8002-clock-time-us-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));probe=decode((ROOT/'build/gx8002-board/flash-probe-candidate.disassembly.txt').read_text());calls=[];cases=0
    def convert(raw):
        value=timer(code,raw&0xffffffff,raw>>32)
        assert value==((raw*1000)&((1<<64)-1))>>10
        calls.append(raw);return value
    for start in (0,0xffffffff,(1<<54)-2048):
        for delta in (5119999,5120000,5120001,1<<33):
            raw=[start,(start+delta)&((1<<64)-1),(start+delta+5120000)&((1<<64)-1)]
            times=[((x*1000)&((1<<64)-1))>>10 for x in raw]
            for states in ((0,0),(2,2),(255,1)):
                args=(1,2,8000000,3);results=(0,0);expected=oracle(args,states,times,results)
                actual=execute(probe,0x1002475c,args,states,raw,results,time_runner=convert)
                assert actual==expected;cases+=1
    return {'evidence':evidence,'timer_cases':cases,'decoded_timer_calls':len(calls),'timer_elf_sha256':sha(path.read_bytes()),'source_admitted':False,
            'limits':['Actual decoded timer conversion drives timeout; raw counter reads scripted. Probe callback remains modeled; no physical timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-probe-timer.json').write_text(json.dumps(r,indent=2)+'\n');print(r['timer_cases'],r['decoded_timer_calls'])
