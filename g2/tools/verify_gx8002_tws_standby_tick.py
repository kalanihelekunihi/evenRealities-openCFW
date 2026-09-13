# SPDX-License-Identifier: MIT
"""Decoded standby countdown feeds TWS tick suspend decisions."""
import json,subprocess
from build_gx8002_tws_standby_candidate import build
from verify_gx8002_tws_standby import verify as qualify,execute as step,STATE,ROOT,decode
from verify_gx8002_tws_tick import verify as tick_qualify,execute as tick

def verify():
    candidate=build();standby=qualify();consumer=tick_qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x1836c','--stop-address=0x183f0',str(path)],text=True));cases=0;suspends=0
    for locked in (0,1):
        memory,_=step(code,0x183c8,0,0,2)
        for frame in range(1,52):
            memory,_=step(code,0x183d8,memory[STATE],memory[STATE+4],0)
            actual=tick(code,consumer['candidate']['bindings'],0,0,0,0,memory[STATE],locked,91)
            expected=[('LvpQueueGet',)]
            if frame>=50:
                expected.append(('LvpPmuSuspendIsLocked',))
                if not locked:expected.append(('LvpPmuSuspend',13));suspends+=1
            assert actual==expected
            assert memory=={STATE:2 if frame<50 else 4,STATE+4:max(50-frame,0)};cases+=1
    return {'candidate':candidate,'standby':standby,'tick':consumer,'sequence_cases':cases,'suspend_requests':suspends,'source_admitted':False,'limits':['Actual decoded standby state result passed to decoded tick across 51 frames for each lock condition. Queue and power calls modeled; suspend request does not prove physical sleep or full application lifecycle.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-standby-tick.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sequence_cases'],r['suspend_requests'])
