# SPDX-License-Identifier: MIT
"""Independent dispatcher oracle, including helper-state mutation."""
import json,subprocess
from itertools import product
from build_gx8002_decoder_default import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_max_decoder import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
STATE=0x20026d2c
INDEX=0x2002e748
CTX=0x20040000
ACT=0x20040100

def verify():
    candidate=build();d=Elf32((ROOT/'build/gx8002-decoder-default/defaults.elf').read_bytes(),'defaults');initial=int.from_bytes(d.contents(next(s for s in d.sections if s['name']=='.decoder_state')),'little');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11e84','--stop-address=0x11ed0',str(wrapper)],text=True));path=ROOT/'build/gx8002-source-candidate/max-decoder/max-decoder.elf';e=Elf32(path.read_bytes(),'decoder');report=json.loads((ROOT/'docs/research/gx8002-max-decoder-source-verification.json').read_text())
    for section in e.sections:
        if section['flags']&2 and section['size']:assert any(row.get('compiled_sha256')==sha(e.contents(section)) for row in report['functions'])
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True));cases=0
    for result,state,index,activation,mutation,value in product((0,1,0xffffffff),(initial,),(0,0xffffffff),(0,ACT,CTX+9),(0,0x102086dc,0x10208a10,0x10208b64,0x10208964),(0,1,255)):
        memory={a+i:0xa5 for a,n in ((STATE-4,12),(INDEX-4,12),(CTX,32),(ACT,16)) for i in range(n)}
        word(memory,STATE,state);word(memory,INDEX,index);memory[ACT+4]=42
        def helper(t,args,m,events):
            a,b,c,d=args
            if t==0x102086dc:events.append(('score',a,b));ret=result
            elif t==0x10208a10:events.append(('strategy',a,word(m,INDEX)));ret=activation
            elif t in (0x10208b64,0x10208964):events.append(('cleanup',t,m[CTX+13]));ret=0xffffffff
            else:raise ValueError('Helper')
            if t==mutation:
                word(m,STATE,value);word(m,INDEX,value);m[CTX+13]=value;m[ACT+4]=value
            return ret
        expected=memory.copy();events=[]
        first=helper(0x102086dc,[CTX,1,0,0],expected,events)
        if first and word(expected,STATE)==1:helper(0x102086dc,[CTX,0,0,0],expected,events)
        word(expected,INDEX,(word(expected,INDEX)+1)&0xffffffff)
        selected=helper(0x10208a10,[CTX,0,0,0],expected,events)
        if selected:
            expected[CTX+13]=expected[selected+4]
            for t in (0x10208b64,0x10208964):helper(t,[0,0,0,0],expected,events)
        for code,entry in ((old,0x11e84),(new,0x102088f8)):
            actual,m,trace=execute(code,entry,CTX,0,memory,helper)
            if (actual,m,[e for e in trace if e[0]!='write_byte'])!=(('return',0),expected,events):raise ValueError(('Decoder mismatch',result,state,index,activation,mutation,value,hex(entry)))
        cases+=1
    return {'candidate':candidate,'consumer_elf_sha256':sha(path.read_bytes()),'decoded_cases':cases,'source_admitted':False,'limits':['Compiled upstream active default feeds stock and authenticated registered decoder with independent control-flow/state oracle; helpers modeled, including synthetic nonzero scorer return to exercise stock minor-pass gate. No nested source-helper or hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-decoder-default-consumer.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
