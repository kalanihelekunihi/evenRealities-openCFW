# SPDX-License-Identifier: MIT
"""Independent bionic arithmetic oracle against decoded stock and C."""
import json,subprocess,math
from itertools import product
from build_gx8002_bionic_run_candidate import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_bionic_run import execute,bits,floating,signed
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e84c
CTX=0x20040000
HEADER=0x20040100
LIST=0x2002e79c

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(w.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x12104','--stop-address=0x12180',str(w)],text=True));new=decode((ROOT/'build/gx8002-bionic-run/candidate.disassembly.txt').read_text());cases=0
    for count,counter,frame,frames,offset in product((0,2,0xffffffff),(0,1,2499,0x7fffffff,0xffffffff),(0,10,0x80000000),(1,10),(0.,145.,149.,150.,float('nan'),float('inf'),float('-inf'))):
        m={a+i:0xa5 for a,n in ((BASE-8,32),(CTX,32),(HEADER,80),(LIST,8)) for i in range(n)};word(m,CTX,HEADER);word(m,HEADER+28,frame);word(m,HEADER+36,frames);word(m,LIST,count);word(m,BASE+12,counter);word(m,BASE+4,bits(offset));wanted=m.copy();events=[]
        elapsed=(frame*frames)&0xffffffff;timeout=((count*1000000)&0xffffffff)>>2;next_counter=(counter+1)&0xffffffff;word(wanted,BASE+12,next_counter)
        if signed((next_counter*elapsed)&0xffffffff)>signed(timeout) and offset<150.:
            word(wanted,BASE+12,0);next_offset=floating(bits(offset+5.));next_offset=150. if next_offset>150. else next_offset;word(wanted,BASE+4,bits(next_offset))
            converted=0 if math.isnan(next_offset) else int(max(-2147483648,min(2147483647,next_offset)))
            events=[(0x1020b3cd,converted&0xffffffff)]
        def helper(t,args,f,sp,mem,trace):
            if t==0x100264dc:return LIST,None
            if t==0x10206c24:trace.append(tuple(args[:2]));return 0,None
            raise ValueError('Helper')
        for code,entry in ((old,0x12104),(new,0x10208b78)):
            result,actual,trace=execute(code,entry,CTX,0,m,helper)
            if (result,actual,[x for x in trace if x[0]!='write_byte'])!=(('return',0),wanted,events):raise ValueError(('Bionic mismatch',count,counter,frame,frames,offset,hex(entry)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Independent wrapped-integer and default binary32 result oracle. Parameter helper and printf modeled; mutation, exception flags/traps and hardware unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-bionic-run-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
