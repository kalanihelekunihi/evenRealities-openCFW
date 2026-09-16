# SPDX-License-Identifier: MIT
"""Compare decoded backup record callbacks with modeled audio/cache/queue helpers."""
import json,re
from itertools import product
from build_gx8002_backup_denoise_record_callback import build,ROOT,BINDINGS
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
CTX=0x20040000
HEADER=0x20041000

def execute(code,entry,delta,index,mics,frames,rate,length,cache_hook=None):
    r={f'r{i}':0xa0000000+i for i in range(32)};r['r0']=index;r['r14']=0x20070000
    initial=r.copy();memory={CTX:HEADER,CTX+8:0,HEADER+8:mics,HEADER+28:length,HEADER+32:rate,HEADER+36:frames}
    saved=None;frame=0;pc=entry;condition=False;trace=[]
    names={v:k for k,v in BINDINGS.items()}
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            m=re.fullmatch(r'r4-r([67]), r15',args);assert m and saved is None
            keys=[f'r{i}' for i in range(4,int(m[1])+1)]+['r15'];saved={k:r[k] for k in keys};frame=len(keys)*4;r['r14']-=frame
        elif op=='pop':
            assert saved is not None;r.update(saved);r['r14']+=frame
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],memory[CTX+8],trace
        elif op in ('lrw','movi','mov'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','mult','lsli','divu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a*b if op=='mult' else a<<b if op=='lsli' else a//b)&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bf','bt','bez'):
            if op=='br' or op=='bf' and not condition or op=='bt' and condition or op=='bez' and r[p[0]]==0:nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            assert address in memory
            if op=='ld.w':r[reg]=memory[address]
            else:memory[address]=r[reg]
            if address<0x20060000:trace.append(('read' if op=='ld.w' else 'write',address,memory[address]))
        elif op=='bsr':
            name=names[int(args,0)+delta];ret=MASK
            if name=='backup_get_context':
                assert r['r1']==r['r14'] and r['r2']==r['r14']+4
                memory[r['r1']]=CTX;memory[r['r2']]=12;event=(name,r['r0'])
            elif name=='backup_get_mic_frame':
                assert r['r0']==CTX and r['r2']==0
                event=(name,r['r0'],r['r1'],r['r2']);ret=0x20050000+r['r1']*0x100
            elif name=='backup_dcache_invalid_range':
                event=(name,r['r0'],r['r1'])
                if cache_hook is not None:cache_hook(r['r0'],r['r1'])
            elif name=='backup_queue_put':
                assert r['r1']==r['r14'];event=(name,r['r0'],memory[r['r1']])
            else:raise AssertionError(name)
            trace.append(event)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=ret
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('Execution bound')

def verify():
    report=build();assert report['fits'];out=ROOT/'build/gx8002-backup-denoise-record-callback'
    old=decode((out/'stock.disassembly.txt').read_text());new=decode((out/'callback.disassembly.txt').read_text());cases=0
    for args in product((0,1,MASK),(0,1,2,4),(0,1,40,0x10001,MASK),(0,16000,48000,MASK),(0,1,10,256,MASK)):
        a=execute(old,0x44694,0x10000000-0x38940,*args);b=execute(new,0x1000bd54,0,*args)
        assert a==b,(args,a,b)
        index,mics,frames,rate,length=args;size=((((frames*rate)&MASK)*length)&MASK)//1000*2&MASK
        calls=[x for x in a[2] if isinstance(x[0],str) and x[0].startswith('backup_')]
        wanted=[('backup_get_context',index)]
        for i in range(mics):wanted.extend([('backup_get_mic_frame',CTX,i,0),('backup_dcache_invalid_range',0x20050000+i*0x100,size)])
        wanted.append(('backup_queue_put',0x2002d2d8,CTX))
        assert a[:2]==(0,index) and calls==wanted
        cases+=1
    result={'candidate':report,'decoded_cases':cases,'source_admitted':False,'limits':['Ordered non-stack field accesses and helper calls agree with stock; independent oracle checks wrapping sample arithmetic, cache ranges and queued pointer.', 'Valid initialized context/header and microphone counts up to four; helpers are modeled without pointer/count mutation. Candidate frame is four bytes larger. No nested helper or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-denoise-record-callback-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['decoded_cases'])
