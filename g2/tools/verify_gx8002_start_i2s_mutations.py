# SPDX-License-Identifier: MIT
"""I2S startup differential shared-state mutation checks."""
import json,subprocess
from itertools import product
from build_gx8002_start_i2s import build,ROOT,IMAGE_SHA,sha,Elf32,DIAGNOSTICS
from execute_gx8002_start_i2s import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
APP=0x2002e8c4
PENDING=0x20026d34

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x1257c','--stop-address=0x126c8',str(path)],text=True));new=decode((ROOT/'build/gx8002-start-i2s/candidate.disassembly.txt').read_text())
    targets={a:n.removeprefix('open_cfw_gx8002_i2s_') for n,a in candidate['bindings'].items() if n.startswith('open_cfw_gx8002_i2s_')};diagnostics={a:n for n,(a,t) in DIAGNOSTICS.items()};cases=0
    reached_cases=0
    for stage,field,value in product(('log','close_log','close','shutdown','padmux','clock_set','initialize','clock_get','open','callback','mode','buffer_size','channel','buffer_base','buffers','format','mclk','lrclk','bits','done'),(0,4,20,24,28,32),(0,7,0xffffffff)):
        m={APP+i:0xa5 for i in range(32)};m[PENDING]=7;word(m,APP+20,0);word(m,APP+4,9)
        size=640;result=0xffffffff;runs=[];hits=[]
        for code,entry in ((old,0x1257c),(new,0x10208ff0)):
            bases=[0];hit=[0]
            def helper(t,a,mem,events,sp):
                if t==0x10206c24:
                    name=diagnostics[a[0]];count=3 if name=='close_log' else 2 if name=='log' else 1
                    events.append(('print',name,*a[1:1+count]))
                    if name==stage:
                        hit[0]+=1
                        if field==32:mem[PENDING]=value&255
                        else:word(mem,APP+field,value)
                    return result
                name=targets[t]
                if name in ('callback','buffers'):events.append((name,a[0],*[word(mem,a[1]+4*i) for i in range(2 if name=='callback' else 3)]))
                elif name=='format':events.append((name,a[0],word(mem,a[1]),*[mem[a[1]+i] for i in range(4,8)],word(mem,a[1]+8)))
                else:
                    count=0 if name in ('shutdown','buffer_size','buffer_base') else 2 if name in ('padmux','clock_set','mode','channel') else 1
                    events.append((name,*a[:count]))
                if name==stage:
                    hit[0]+=1
                    if field==32:mem[PENDING]=value&255
                    else:word(mem,APP+field,value)
                if name=='clock_get':return 24576000
                if name=='buffer_size':return size
                if name=='buffer_base':base_result=0x20050000+bases[0]*4096;bases[0]+=1;return base_result
                return result
            ret,actual,events=execute(code,entry,[],m,helper);events=[e for e in events if e[0]!='write_byte']
            runs.append((ret,actual,events));hits.append(hit[0])
        if runs[0]!=runs[1] or hits[0]!=hits[1]:raise ValueError(('Mutation mismatch',stage,field,value,runs))
        cases+=1;reached_cases+=bool(hits[0])
    return {'candidate':candidate,'cases':cases,'cases_reaching_mutation':reached_cases,'source_admitted':False,'limits':['Differential shared-state mutations at modeled helper boundaries; configuration pointer mutations and nested hardware behavior remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-start-i2s-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
