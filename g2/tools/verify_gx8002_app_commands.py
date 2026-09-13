# SPDX-License-Identifier: MIT
"""Independent eleven-record constructor oracle and cross-record mutations."""
import json,subprocess
from itertools import product
from build_gx8002_app_commands import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_app_commands import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
IDS=(368,369,258,263,265,266,267,268,269,270,271)
NAMES=(0x1020b698,0x1020b6a3,0x1020b6b2,0x1020b6ba,0x1020b6c8,0x1020b6db,0x1020b6ef,0x1020b6fc,0x1020b70b,0x1020b71a,0x1020b727)

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x127e4','--stop-address=0x12968',str(path)],text=True));new=decode((ROOT/'build/gx8002-app-commands/candidate.disassembly.txt').read_text());cases=0
    for mutation,field,value in product((-1,0,5,9),range(7),(0,7,0xffffffff)):
        rows=[[0,ident,0x2002e8f0 if i in (6,10) else 0,32 if i in (6,10) else 0,0,0x10209430,NAMES[i]] for i,ident in enumerate(IDS)]
        expected=[]
        for i in range(11):
            expected.append(('register',i,tuple(rows[i])))
            if i==mutation:rows[i+1][field]=value
        for code,entry in ((old,0x127e4),(new,0x10209258)):
            index=[0];clears=[0];base=[None]
            def helper(t,a,mem,events,sp):
                if t==0x102099cc:
                    if a[1:3]!=[0,28]:raise ValueError('Clear arguments')
                    if base[0] is None:base[0]=a[0]
                    if a[0]!=base[0]+28*clears[0]:raise ValueError('Clear order')
                    clears[0]+=1
                    for offset in range(28):mem[a[0]+offset]=0
                    return a[0]
                if t!=0x102082ac or clears[0]!=11 or a[0]!=base[0]+index[0]*28:raise ValueError('Registration order')
                i=index[0];events.append(('register',i,tuple(word(mem,a[0]+4*j) for j in range(7))))
                if i==mutation:word(mem,a[0]+28+4*field,value)
                index[0]+=1;return 0xffffffff
            ret,actual,events=execute(code,entry,[],{},helper);events=[e for e in events if e[0]!='write_byte']
            if ret[0]!='return' or actual or events!=expected or index[0]!=11:raise ValueError(('Constructor mismatch',mutation,field,value,hex(entry),events,expected))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent record/order oracle with next-record mutations; memset modeled, callback and nested registration behavior unqualified; void return unspecified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-app-commands-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
