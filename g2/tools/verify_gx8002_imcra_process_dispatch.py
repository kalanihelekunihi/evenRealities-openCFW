# SPDX-License-Identifier: MIT
"""Decoded composed entry dispatch/ABI check; stage bodies are models."""
import json,re
from build_gx8002_imcra_process import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def signed(x):return x if x<0x80000000 else x-0x100000000

def execute(code,symbols,bins,frame,shift,mutate):
    state,inputs,outputs,power=0x21000000,0x21010000,0x21020000,0x21030000
    memory={state+28:bins&M,state+32:frame,state+64:power,state+116:0}
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=state,r1=inputs,r2=outputs,r14=0x30000000,r15=0x12345678)
    initial=r.copy();stack={};calls=[];pc=symbols['process'];reverse={v:k for k,v in symbols.items()}
    argc={'prepare':2,'power_spectrum':2,'first_frame':2,'prior_update':3,'smooth':2,'minimum_mask':2,'masked_smooth':3,'probability':2,'noise_update':2,'history_rotate':3,'synthesize':4}
    for _ in range(150):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r9, r15'
            r['r14']-=28
            for i,reg in enumerate([*range(4,10),15]):stack[r['r14']+i*4]=r[f'r{reg}']
        elif op=='pop':
            assert args=='r4-r9, r15'
            for i,reg in enumerate([*range(4,10),15]):r[f'r{reg}']=stack[r['r14']+i*4]
            r['r14']+=28
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return calls
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args);assert m,args
            reg,base,offset=m.groups();r[reg]=memory[r[base]+int(offset,0)]
        elif op in ('bnez','blsz'):
            if (r[p[0]]!=0 if op=='bnez' else signed(r[p[0]])<=0):nxt=int(p[1],0)
        elif op=='bsr':
            stage=reverse[int(args,0)];calls.append((stage,*(r[f'r{i}'] for i in range(argc[stage]))))
            if mutate and stage=='first_frame':memory[state+28]=3;memory[state+32]=7
            if mutate and stage=='smooth':memory[state+116]=1
            if mutate and stage=='history_rotate':memory[state+28]=2
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0x60000000+i
            r['r0']=shift&M if stage=='prepare' else 0xdeadbeef
            r['r15']=nxt
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-imcra-process'
    elf=Elf32((out/'prepare.elf').read_bytes(),'process')
    prefix='open_cfw_gx8002_imcra_'
    symbols={s['name'][len(prefix):]:s['value'] for s in elf.symbols() if s['name'].startswith(prefix) and s['section'] not in (0,0xfff1)}
    code=decode((out/'prepare.disassembly.txt').read_text());cases=0
    for bins in (0,1,257):
        for frame in (0,1,7):
            for shift in (-9,-1,0,1):
                for mutate in (False,True):
                    actual=execute(code,symbols,bins,frame,shift,mutate)
                    state=0x21000000;expected=[('prepare',state,0x21010000),('power_spectrum',state,shift&M)]
                    n=bins;f=frame
                    if frame==0:
                        expected.append(('first_frame',state,n))
                        if mutate:n=3;f=7
                    if n>0:expected.append(('prior_update',state,0x21030000,n))
                    expected.extend([('smooth',state,n),('minimum_mask',state,n),('masked_smooth',state,n,1 if mutate else 0)])
                    if n>0:expected.extend([('probability',state,n),('noise_update',state,n)])
                    expected.extend([('history_rotate',state,n,f),('synthesize',state,0x21020000,2 if mutate else n,shift&M)])
                    assert actual==expected,(bins,frame,shift,mutate)
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Composed candidate entry dispatch against authored stage-order/argument expectations, with caller clobbers and saved-register checks.', 'Stage bodies not executed; not a stock whole-function comparison. Mutations test wrapper reloads, not stock equivalence under mutation.', 'No shared stage stack, physical FPU, nested FFT or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-process-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
