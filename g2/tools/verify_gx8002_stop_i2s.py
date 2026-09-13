# SPDX-License-Identifier: MIT
"""Shutdown independent state machine oracle including helper mutations."""
import json,subprocess
from itertools import product
from build_gx8002_stop_i2s import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_stop_i2s import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
APP=0x2002e8c4
PENDING=0x20026d34

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x126c8','--stop-address=0x12748',str(path)],text=True));new=decode((ROOT/'build/gx8002-stop-i2s/candidate.disassembly.txt').read_text());cases=0
    for enabled,handle,stage,field,value in product((0,1),(7,0xffffffff),('none','log','pad7','pad10','close_log','close','shutdown'),(0,4,20,24,28,32),(0,7,0xffffffff)):
        m={APP+i:0xa5 for i in range(32)};m[PENDING]=7;word(m,APP+20,enabled);word(m,APP+4,handle)
        def mutate(name,mem):
            if name==stage:
                if field==32:mem[PENDING]=value&255
                else:word(mem,APP+field,value)
        expected=m.copy();wanted=[]
        def call(name,*args):wanted.append((name,*args));mutate(name,expected)
        call('log',0x1020b431,307)
        if word(expected,APP+20):
            word(expected,APP+20,0);expected[PENDING]=0
            for pin in range(7,11):call('pad'+str(pin),pin,1)
            if word(expected,APP+4)!=0xffffffff:
                call('close_log',0x1020b431,329,word(expected,APP+4));call('close',word(expected,APP+4));call('shutdown');word(expected,APP+4,0xffffffff)
            word(expected,APP+24,0);word(expected,APP+28,0);word(expected,APP,0)
        def helper(t,a,mem,events,sp):
            if t==0x10206c24:name='log' if a[0]==0x1020b536 else 'close_log';args=a[1:3] if name=='log' else a[1:4]
            elif t==0x102065dc:name='pad'+str(a[0]);args=a[:2]
            elif t==0x102053b0:name='close';args=a[:1]
            elif t==0x10205574:name='shutdown';args=[]
            else:raise ValueError('Helper')
            events.append((name,*args));mutate(name,mem);return 0xffffffff
        for code,entry in ((old,0x126c8),(new,0x1020913c)):
            ret,actual,events=execute(code,entry,[],m,helper);events=[e for e in events if e[0]!='write_byte']
            if ret[0]!='return' or (actual,events)!=(expected,wanted):raise ValueError(('Shutdown mismatch',enabled,handle,stage,field,value,hex(entry),events,wanted))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent final-state and helper-argument/order oracle, shared-state mutations and preserved integer ABI; void return value intentionally unspecified; nested hardware behavior unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stop-i2s-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
