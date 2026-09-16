# SPDX-License-Identifier: MIT
"""Compare backup timer and division instructions with compiled C and arithmetic."""
import json, random, subprocess
from build_gx8002_backup_clock_time_us import build, ROOT, Elf32, sha
from verify_gx8002_clock_time_us_candidate import execute as source, decode
from execute_gx8002_clock_time_stock import execute as stock
from analyze_gx8002_upstream_objects import IMAGE_SHA


def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def code(lo,hi):return decode(subprocess.check_output([pre,'-D',f'--start-address={lo:#x}',f'--stop-address={hi:#x}',str(path)],text=True))
    timer=code(0x3d9b0,0x3da0c);divider=code(0x44f10,0x44fe4)
    new=decode((ROOT/'build/gx8002-backup-clock-time-us/timer.disassembly.txt').read_text())
    rng=random.Random(909);values=[0,1,1023,1024,4294967,4294968,0xffffffff,1<<32,(1<<64)//1000-1,(1<<64)//1000,(1<<64)//1000+1,(1<<64)-1]+[rng.getrandbits(64) for _ in range(2048)]
    for ticks in values:
        low=ticks&0xffffffff;high=ticks>>32;want=((ticks*1000)&((1<<64)-1))>>10
        assert stock(timer,low,high,divider,entry=0x3d9b0,divider_entry=0x44f10,divider_target=0x44f10)==source(new,low,high,entry=0x10005070)==want
    report={'candidate':evidence,'cases':len(values),'source_admitted':False,'limits':['Stock division executes in a marshalled helper frame. Ordered reads and ABI checked; hardware timing and composed PLL execution pending.']}
    (ROOT/'docs/research/gx8002-backup-clock-time-us-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'])
