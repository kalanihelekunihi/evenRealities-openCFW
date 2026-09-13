# SPDX-License-Identifier: MIT
"""Compare decoded MAX scorer under bounded helper-induced state changes."""
import json, subprocess
from itertools import product
from verify_gx8002_max_score import ROOT, BASE, CTX, HEADER, PARAM, OUTPUT, build, Elf32, sha, IMAGE_SHA, decode, word, execute, bits

def verify():
    candidate=build()
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11c68','--stop-address=0x11e0c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-max-score/candidate.disassembly.txt').read_text())
    fields={BASE+4:(0,9),BASE+88:(0,1,2),BASE+92:(PARAM,PARAM+176),BASE+96:(0,777),CTX+8:(0,456),CTX+16:(OUTPUT,OUTPUT+8),HEADER+68:(0,16),OUTPUT:(bits(0.1),bits(1.5)),PARAM+76:(0,1500),PARAM+84:(0,1),PARAM+80:(0,99),BASE+8:(0,255)}
    cases=0
    exercised=0
    mutation_calls=0
    for target,major,(address,values) in product((0x102099cc,0x10025608,0x10208c60,0x10208b78,0x10208b58,0x10208980,0x10206c24,0x10208b68),(0,1),fields.items()):
        for value in values:
            memory={a+i:0 for a,n in ((BASE-16,132),(CTX,32),(HEADER,80),(PARAM,352),(OUTPUT,16)) for i in range(n)}
            word(memory,BASE+88,2);word(memory,BASE+92,PARAM)
            word(memory,CTX,HEADER);word(memory,CTX+8,123);word(memory,CTX+16,OUTPUT);word(memory,HEADER+68,8)
            for i in range(4):
                word(memory,OUTPUT+4*i,bits(1.0));word(memory,PARAM+88*i+76,500)
                word(memory,PARAM+88*i+80,40+i);word(memory,PARAM+88*i+84,i%2)
            def helper(t,args,f,sp,m,events):
                a,b,c,d=args
                result=0;fr=None
                if t==0x102099cc:
                    events.append(('clear',a,b,c))
                    for i in range(c):m[a+i]=b&255
                    result=a
                elif t==0x10025608:events.append(('invalidate',a,b))
                elif t==0x10208c60:events.append(('output',a));result=a
                elif t==0x10208b78:events.append(('bionic',a,b,f['fr0'],f['fr1'],c))
                elif t==0x10208b58:events.append(('offset',a,f['fr0']));fr=bits(0.75)
                elif t==0x10208980:events.append(('insert',a,b,f['fr0'],c,d))
                elif t==0x10206c24:events.append(('print',a,b,c,d,word(m,sp),word(m,sp+4),word(m,sp+8)))
                elif t==0x10208b68:events.append(('reset',))
                else:raise ValueError(('Helper',hex(t)))
                if t==target:
                    word(m,address,value)
                    hits[0]+=1
                return result,fr
            results=[]
            hits=[0]
            for code,entry in ((old,0x11c68),(new,0x102086dc)):
                result,m,events=execute(code,entry,CTX,major,memory,helper)
                results.append((result,m,[e for e in events if e[0]!='write_byte']))
            if results[0]!=results[1]:raise ValueError(('Mutation mismatch',hex(target),major,hex(address),value,results[0][2],results[1][2]))
            cases+=1
            exercised+=bool(hits[0])
            mutation_calls+=hits[0]
    return {'candidate':candidate,'decoded_mutation_cases':cases,'cases_reaching_mutation':exercised,'mutated_helper_calls':mutation_calls,'source_admitted':False,'limits':['Differential stock/source only; one field changed after selected modeled helpers. No independent mutation oracle, exceptional conversion or hardware claim.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-max-score-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_mutation_cases'])
