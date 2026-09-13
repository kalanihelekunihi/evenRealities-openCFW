# SPDX-License-Identifier: MIT
"""Notification stamp independent helper/state/write oracle."""
import json,subprocess
from itertools import product
from build_gx8002_notification_stamp import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_app_reply import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12968','--stop-address=0x12980',str(path)],text=True));new=decode((ROOT/'build/gx8002-notification-stamp/candidate.disassembly.txt').read_text());cases=0
    for clock,result,mutation in product((0,1,0x7fffffff,0x80000000,0xffffffff),(0,0xffffffff),(False,True)):
        seed={0x2002e910+i:0xa5 for i in range(4)};expected=seed.copy();word(expected,0x2002e910,clock)
        wanted=[('gpio',2,0),('clock',)]+[('write_byte',0x2002e910+i,(clock>>(8*i))&255) for i in range(4)]
        def helper(t,a,m,e):
            if t==0x10205f88:e.append(('gpio',*a[:2]));value=result
            elif t==0x10025930:e.append(('clock',));value=clock
            else:raise ValueError('Helper')
            if mutation:word(m,0x2002e910,123)
            return value
        for code,entry in ((old,0x12968),(new,0x102093dc)):
            ret,actual,events=execute(code,entry,[],seed,helper)
            if ret[0]!='return' or (actual,events)!=(expected,wanted):raise ValueError('Stamp mismatch')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent GPIO-before-clock and exact timestamp store oracle; helper mutations/ignored GPIO failure and integer ABI checked, nested hardware unqualified. Void return unspecified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-notification-stamp-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
