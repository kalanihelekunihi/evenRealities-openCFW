# SPDX-License-Identifier: MIT
"""Independent event-path oracle against stock and native macOS C build."""
import json,subprocess
from itertools import product
from build_gx8002_sample_event import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_sample_event import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
EVENT,CONTEXT,STATE,APP=0x20040000,0x20041000,0x20026d30,0x2002e8c4

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(w.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x12490','--stop-address=0x1257c',str(w)],text=True));new=decode((ROOT/'build/gx8002-sample-event/candidate.disassembly.txt').read_text());cases=0
    for event,vad,last,enabled,pending,outputs,result in product((0,91,100,101),(0,3,255),(0,3),(0,1),(0,1),(False,True),(0,0xffffffff)):
        m={a+i:0xa5 for a,n in ((EVENT,8),(CONTEXT,32),(STATE,8),(APP,28)) for i in range(n)}
        for a,v in ((EVENT,event),(EVENT+4,17),(CONTEXT,0x20042000),(STATE,last),(APP+4,7),(APP+20,enabled),(APP+24,0x20050000)):word(m,a,v)
        m[CONTEXT+12]=vad;m[STATE+4]=pending;expected=m.copy();wanted=[('lookup',17)]
        if vad&7!=last:wanted.append(('vad',vad&7));word(expected,STATE,vad&7)
        if event in (100,101):wanted.extend([('print',0x1020b4c7 if event==100 else 0x1020b4d9),('notify',event)])
        if event==91 and enabled and pending:
            start=320 if outputs else (-0x20050000)&0xffffffff;end=(start+(320 if outputs else 0)-1)&0xffffffff
            wanted.extend([('print',0x1020b4ea,17,1),('mic',0x20042000,0,17),('mic',0x20042000,1,17),('print',0x1020b50a,start,end),('frame',7,start,end)]);expected[STATE+4]=0
        def helper(t,a,mem,trace,sp):
            if t==0x10206ec8:trace.append(('lookup',a[0]));word(mem,a[1],CONTEXT);word(mem,a[2],99)
            elif t==0x1020979c:trace.append(('vad',a[0]))
            elif t==0x1020975c:trace.append(('notify',a[0]))
            elif t==0x10206c24:trace.append(tuple(['print',a[0]]+(a[1:3] if a[0] in (0x1020b4ea,0x1020b50a) else [])))
            elif t==0x10208e80:
                trace.append(('mic',*a[:3]))
                if outputs:word(mem,a[3],0x20050140+a[1]*4096);word(mem,word(mem,sp),320)
            elif t==0x10205488:trace.append(('frame',a[0],word(mem,a[1]),word(mem,a[1]+4)))
            else:raise ValueError(('Helper',hex(t)))
            return result
        for code,entry in ((old,0x12490),(new,0x10208f04)):
            ret,actual,trace=execute(code,entry,[EVENT],m,helper)
            trace=[x for x in trace if x[0]!='write_byte']
            if (ret,actual,trace)!=(('return',0),expected,wanted):raise ValueError(('Event mismatch',event,vad,last,enabled,pending,outputs,result,hex(entry),ret,trace,wanted))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent baseline includes ignored helper failures and unwritten microphone outputs; helper mutations and nested hardware behavior remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-sample-event-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
