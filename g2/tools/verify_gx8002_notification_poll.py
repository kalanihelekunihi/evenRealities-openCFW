# SPDX-License-Identifier: MIT
"""Independent notification timeout oracle, including helper mutations and wraparound."""
import json, subprocess
from itertools import product
from build_gx8002_notification_poll import build, ROOT, IMAGE_SHA, sha, Elf32
from execute_gx8002_event_notify import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build(); path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12d54','--stop-address=0x12d80',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-notification-poll/candidate.disassembly.txt').read_text())
    address=0x2002e910; cases=0
    for initial,delta,mutation,gpio_mutation,result in product((0,1,0xffffffd0,0xffffffff),(0,59,60,61,62,0xffffffff),(None,0,17),(False,True),(0,0xffffffff)):
        now=(initial+delta)&0xffffffff
        memory={address+i:0 for i in range(4)};word(memory,address,initial)
        expected=memory.copy(); trace=[]
        if initial:
            trace.append(('clock',))
            if mutation is not None:word(expected,address,mutation)
            if ((now-word(expected,address))&0xffffffff)>60:
                trace.append(('gpio',2,1))
                if gpio_mutation:word(expected,address,123)
                word(expected,address,0)
                trace.extend(('write_byte',address+i,0) for i in range(4))
        def helper(t,a,m,e):
            if t==0x10025930:
                e.append(('clock',))
                if mutation is not None:word(m,address,mutation)
                return now
            if t==0x10205f88:
                e.append(('gpio',*a[:2]))
                if gpio_mutation:word(m,address,123)
                return result
            raise ValueError('Unknown helper')
        for code,entry in ((old,0x12d54),(new,0x102097c8)):
            ret,m,events=execute(code,entry,[],memory,helper)
            if ret!=('return',0) or m!=expected or events!=trace:raise ValueError((initial,delta,mutation,ret,events,trace))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Integer ABI, unsigned timeout boundary and helper mutations checked; nested helpers and hardware unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-notification-poll-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
