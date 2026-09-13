# SPDX-License-Identifier: MIT
"""Independent response field/order oracle and enqueue mutation checks."""
import json,subprocess
from itertools import product
from build_gx8002_app_reply import ROOT,IMAGE_SHA,sha,Elf32
from probe_gx8002_reply_sdk_types import probe as build
from execute_gx8002_app_reply import execute
from verify_gx8002_memcpy_source import decode
STATE,VALUE=0x20026d5c,0x2002e914

def verify():
    candidate=build();defaults_elf=Elf32((ROOT/'build/gx8002-reply-defaults/defaults.elf').read_bytes(),'defaults');defaults=defaults_elf.contents(next(s for s in defaults_elf.sections if s['name']=='.reply_packet'));path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12980','--stop-address=0x129bc',str(path)],text=True));new=decode((ROOT/'build/gx8002-reply-sdk-types/app_reply.disassembly.txt').read_text());cases=0
    for kind,command,value,mutation,result in product((0,1,2,0xffffffff),(0,112,0x100,0x200,0xffff,0x10000,0xffffffff),(0,1,0xffff,0x12345678),(False,True),(0,0xffffffff)):
        m={STATE+i:v for i,v in enumerate(defaults)};m.update({VALUE+i:0xa5 for i in range(2)});expected=m.copy();wanted=[]
        for address,size,data in ((VALUE,2,value),(STATE+7,1,1),(STATE+16,4,VALUE),(STATE+4,2,command|(0x300 if kind==1 else 0x200)),(STATE+24,4,2)):
            for i in range(size):expected[address+i]=(data>>(8*i))&255;wanted.append(('write_byte',address+i,expected[address+i]))
        wanted.append(('enqueue',STATE))
        if mutation:expected[STATE+7]=0;expected[VALUE]=99
        def helper(t,a,mem,events):
            if t!=0x102083bc or a[0]!=STATE:raise ValueError('Enqueue')
            events.append(('enqueue',a[0]))
            if mutation:mem[STATE+7]=0;mem[VALUE]=99
            return result
        for code,entry in ((old,0x12980),(new,0x102093f4)):
            ret,actual,events=execute(code,entry,[kind,command,value],m,helper)
            if (ret,actual,events)!=(('return',0),expected,wanted):raise ValueError(('Reply mismatch',kind,command,value,mutation,result,hex(entry),events,wanted))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent field/write-order oracle, integer ABI, ignored enqueue errors and helper mutations; nested enqueue/hardware behavior unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-reply-defaults-response-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
