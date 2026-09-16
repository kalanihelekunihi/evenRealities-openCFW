# SPDX-License-Identifier: MIT
"""Decoded synthesis helper-call block; helper effects explicitly modeled."""
import json,re,subprocess
from build_gx8002_imcra_synthesize import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,source,length,forward,peak,mutate):
    state=0x21000000;spectrum=0x21010000;work=0x21020000
    memory={state+24:length&M,state+56:work,state+60:spectrum}
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r4=state,r6=state,r7=spectrum,r5=forward&M,r9=forward&M)
    pc=0x10016470 if source else 0x4ed9c;stop=0x100164a6 if source else 0x4edd4
    names={0x46c04:'peak',0x46bcc:'shift',0x478a4:'inverse'}
    if source:names={k-0x38940+0x10000000:v for k,v in names.items()}
    trace=[];calls=[]
    for _ in range(80):
        if pc==stop:return trace,calls,memory
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='ld.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args);assert m,args
            reg,base,offset=m.groups();address=r[base]+int(offset,0);r[reg]=memory[address];trace.append(('read',address,r[reg]))
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addi','subi','subu'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op=='addi' else a-b)&M
        elif op=='bsr':
            name=names[int(args,0)];arguments=tuple(r[f'r{i}'] for i in range(2 if name=='peak' else 3));calls.append((name,*arguments));trace.append(('call',name,*arguments))
            if mutate and len(calls)==1:memory[state+24]=(length+4)&M
            if mutate and len(calls)==2:
                memory[state+56]=work+128;memory[state+60]=spectrum+128
            if mutate and name=='inverse':
                memory[state+56]=work+256;memory[state+24]=(length+8)&M
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0x60000000+i
            r['r0']=peak&M if name=='peak' else 0xdeadbeef
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ed9c','--stop-address=0x4edd4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-synthesize/prepare.disassembly.txt').read_text());cases=0
    for length in (0,1,2,512,0xfffffffe,0xffffffff):
        for forward in range(-9,2):
            for peak in (-15,-9,-1,0,1):
                for mutate in (False,True):
                    a=execute(old,False,length,forward,peak,mutate);b=execute(new,True,length,forward,peak,mutate)
                    assert a==b,(length,forward,peak,mutate)
                    assert a[1][0]==('peak',0x21010000,(length+2)&M)
                    assert a[1][1]==('shift',0x21010000,(length+2)&M,peak&M)
                    assert a[1][2]==('inverse',0x2001700c,0x21010000+(128 if mutate else 0),0x21020000+(128 if mutate else 0))
                    assert a[1][3]==('shift',0x21020000+(256 if mutate else 0),(length+(8 if mutate else 0))&M,(-9-forward-peak)&M)
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Exact decoded reads/helper arguments with caller register clobbers and pointer/count mutations.', 'Helpers not executed; wide counts exercise argument arithmetic only, not valid allocations or shift semantics.', 'No full synthesis ABI, nested FFT execution or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-synthesis-calls-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
