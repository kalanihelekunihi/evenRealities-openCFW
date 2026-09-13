# SPDX-License-Identifier: MIT
"""Stock/source differential helper-boundary mutation checks."""
import json,subprocess
from itertools import product
from verify_gx8002_sample_event import ROOT,build,Elf32,sha,IMAGE_SHA,decode,execute,word,EVENT,CONTEXT,STATE,APP

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12490','--stop-address=0x1257c',str(path)],text=True));new=decode((ROOT/'build/gx8002-sample-event/candidate.disassembly.txt').read_text())
    cases=hit=0
    stages=('lookup','vad','hey','hi','notify','start','mic0','mic1','range','frame')
    for event,stage,field,value in product((91,100,101),stages,('id','index','vad','last','pending','enabled','base','handle','header'),(0,101,0xffffffff)):
        m={a+i:0xa5 for a,n in ((EVENT,8),(CONTEXT,32),(STATE,8),(APP,28)) for i in range(n)}
        for a,v in ((EVENT,event),(EVENT+4,17),(CONTEXT,0x20042000),(STATE,0),(APP+4,7),(APP+20,1),(APP+24,0x20050000)):word(m,a,v)
        m[CONTEXT+12]=3;m[STATE+4]=1
        runs=[];reached=[]
        for code,entry in ((old,0x12490),(new,0x10208f04)):
            count=[0]
            def helper(t,a,mem,trace,sp):
                if t==0x10206ec8:
                    label='lookup';trace.append((label,a[0]));word(mem,a[1],CONTEXT);word(mem,a[2],99)
                elif t in (0x1020979c,0x1020975c):
                    label='vad' if t==0x1020979c else 'notify';trace.append((label,a[0]))
                elif t==0x10206c24:
                    label={0x1020b4c7:'hey',0x1020b4d9:'hi',0x1020b4ea:'start',0x1020b50a:'range'}[a[0]];trace.append((label,*a[1:3]) if label in ('start','range') else (label,))
                elif t==0x10208e80:
                    label='mic'+str(a[1]);trace.append((label,*a[:3]));word(mem,a[3],0x20050140+a[1]*4096);word(mem,word(mem,sp),320)
                elif t==0x10205488:label='frame';trace.append((label,a[0],word(mem,a[1]),word(mem,a[1]+4)))
                else:raise ValueError('Helper')
                if label==stage:
                    count[0]+=1
                    address={'id':EVENT,'index':EVENT+4,'vad':CONTEXT+12,'last':STATE,'pending':STATE+4,'enabled':APP+20,'base':APP+24,'handle':APP+4,'header':CONTEXT}[field]
                    if field in ('vad','pending'):mem[address]=value&255
                    else:word(mem,address,value)
                return 0xffffffff
            ret,actual,trace=execute(code,entry,[EVENT],m,helper)
            runs.append((ret,actual,[x for x in trace if x[0]!='write_byte']));reached.append(count[0])
        if runs[0]!=runs[1] or reached[0]!=reached[1]:raise ValueError(('Mutation mismatch',event,stage,field,value,runs))
        cases+=1;hit+=bool(reached[0])
    return {'candidate':candidate,'cases':cases,'cases_reaching_mutation':hit,'source_admitted':False,'limits':['Differential mutations at modeled helper boundaries; no device timing or nested helper execution qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-sample-event-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['cases_reaching_mutation'])
