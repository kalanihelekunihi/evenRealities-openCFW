#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify system startup ordering with modeled returning service calls."""
import contextlib
import io
import itertools
import json
import subprocess
from compare_gx8002_system_mpu import verify as verify_mpu, execute, ROOT, decode


def verify():
    with contextlib.redirect_stdout(io.StringIO()):
        mpu=verify_mpu()
    out=ROOT/'build/gx8002-system'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),
        '-D','--start-address=0x15560','--stop-address=0x15604',str(out/'stock.elf')],text=True))
    new=decode((out/'system.disassembly.txt').read_text());cases=0
    for values in itertools.product((0,0xffffffff,0x55555555,0xaaaaaaaa),repeat=4):
        c=dict(zip((18,19,20,21),values))
        prefix=[['read',19,c[19]],['read',20,c[20]],['read',21,c[21]],
                ['write',21,c[21]&0xfffffff8],['write',19,(c[19]&0xfefffcfe)|0x300],
                ['write',20,(c[20]&0xfff)|0x3f],['read',18,c[18]],['write',18,c[18]|3]]
        for mode in (0,1,2,0xffffffff):
            expected=prefix+[['call',0x10025a88],['call',0x10024984]]
            if mode==0:expected+=[['call',0x10023528]]
            expected += [['call',0x10025cbc],['write',1,0x10023400],['mmio',0xe000ec10,255]]
            for i in range(4):
                expected += [['mmio',0xe000e300+i*4,0],['mmio',0xe000e280+i*4,0xffffffff]]
            expected += [['enable','ee','ie']]
            for seed in (0,0xffffffff):
                if execute(old,0x15560,c,True,mode,0x1000dfec,seed)!=expected or execute(new,0x1002354c,c,True,mode,0,seed)!=expected:
                    raise ValueError('system initialization trace mismatch')
                cases+=1
    report={'mpu':mpu,'cases':cases,'source_admitted':False,
            'limits':['External service implementations are modeled as returning with caller-saved register clobbers.',
                      'Checks fixed register/MMIO ordering and mode branch, not physical hardware effects or timing.']}
    (ROOT/'docs/research/gx8002-system-initialize-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases)
    return report


if __name__=='__main__':verify()
