# SPDX-License-Identifier: MIT
"""Independent event notification helper order and argument oracle."""
import json,subprocess
from itertools import product
from build_gx8002_event_notify import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_event_notify import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12ce8','--stop-address=0x12cfc',str(path)],text=True));new=decode((ROOT/'build/gx8002-event-notify/candidate.disassembly.txt').read_text());cases=0
    for event,result in product((0,91,100,101,0xffff,0x80000000,0xffffffff),(0,1,0xffffffff)):
        def helper(t,a,m,e):
            if t==0x102093dc:e.append(('stamp',))
            elif t==0x102093f4:e.append(('reply',*a[:3]))
            else:raise ValueError('Helper')
            return result
        for code,entry in ((old,0x12ce8),(new,0x1020975c)):
            ret,m,events=execute(code,entry,[event],{},helper)
            if ret[0]!='return' or m or events!=[('stamp',),('reply',1,12,event)]:raise ValueError('Event notify mismatch')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Original event preserved across clobbering helper and ignored results; integer ABI checked, void return unspecified. Nested behavior unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-event-notify-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
