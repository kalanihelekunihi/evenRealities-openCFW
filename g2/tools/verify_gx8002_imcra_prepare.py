# SPDX-License-Identifier: MIT
"""Bounded decoded processing-prefix comparison with explicit helper models."""
import json, random, re, subprocess
from build_gx8002_imcra_prepare import build, ROOT
from verify_gx8002_memcpy_source import decode
M = 0xffffffff

def signed(v, bits=32):
    v &= (1 << bits)-1
    return v-(1 << bits) if v & (1 << (bits-1)) else v

def execute(code, source, values, window, hop, padding, mutate):
    state, history, coefficients, work, output, incoming = [0x21000000+i*0x10000 for i in range(6)]
    memory = {}; trace = []; calls = []
    def put(a, v, size):
        for i in range(size): memory[a+i] = (v >> (8*i)) & 255
    def get(a, size):
        return sum(memory[a+i] << (8*i) for i in range(size))
    frame = len(values)
    for index, value in {3:frame,4:frame+padding,5:hop,6:frame+padding,9:history,12:coefficients,14:work,15:output}.items(): put(state+index*4,value,4)
    for base, data in ((history, values), (coefficients, window), (incoming, values[::-1])):
        for i,v in enumerate(data): put(base+2*i,v,2)
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r0=state,r1=incoming,r2=output,r14=0x30000000)
    pc=0x10015d34 if source else 0x4e674; stop=0x10015ddc if source else 0x4e71a
    condition=False; shift=None
    helpers = {0x422a8:'move',0x49d04:'clear',0x46c04:'peak',0x46bcc:'shift',0x478a4:'fft'}
    if source: helpers={a-0x38940+0x10000000:n for a,n in helpers.items()}
    for _ in range(frame*30+300):
        if pc==stop:
            return trace, calls, memory, r['r5']
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','fsts'): pass # Prefix only: stack/ABI tested separately, not here.
        elif op in ('mov','movi','lrw'): r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addu','subu','addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op.startswith('add') else a-b)&M
        elif op in ('lsli','lsri','asri'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=((a<<b) if op=='lsli' else (signed(a)>>b if op=='asri' else a>>b))&M
        elif op in ('ld.w','ld.h','st.h','ldbi.h','stbi.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)(?:,\s*(0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,offset=m.groups();a=r[base]+int(offset or '0',0);size=4 if op=='ld.w' else 2
            if op.startswith('ld'): r[reg]=get(a,size);trace.append(('read',a,size,r[reg]))
            else:put(a,r[reg],size);trace.append(('write',a,size,r[reg]&0xffff))
            if 'bi.' in op:r[base]+=size
        elif op=='mulsh':r[p[0]]=(signed(r[p[-2] if len(p)==3 else p[0]] ,16)*signed(r[p[-1]],16))&M
        elif op=='sext':
            high,low=int(p[2],0),int(p[3],0);r[p[0]]=signed(r[p[1]]>>low,high-low+1)&M
        elif op=='max.s32':r[p[0]]=max(signed(r[p[1]]),signed(r[p[2]]))&M
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(p[0],0)
        elif op in ('blsz','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0):nxt=int(p[1],0)
        elif op=='bsr':
            name=helpers[int(args,0)];a,b,c=r['r0'],r['r1'],r['r2']
            calls.append((name,a,b) if name=='peak' else (name,a,b,c))
            result=0
            if name=='move':
                data=[get(b+i,1) for i in range(c)]
                for i,v in enumerate(data):put(a+i,v,1)
                result=a
                if mutate and len(calls)==1:put(state+20,max(0,hop-1),4)
            elif name=='clear':
                for i in range(c):put(a+i,0,1)
                result=a
            elif name=='peak':
                peak=max(abs(signed(get(a+i*2,2),16)) for i in range(max(1,b)))
                result=peak.bit_length()-15 if peak else -15
            elif name=='shift':
                shift=signed(c)
                for i in range(b):
                    v=signed(get(a+i*2,2),16);put(a+i*2,v>>shift if shift>0 else v<<-shift,2)
                if mutate:put(state+60,output+128,4)
            elif name=='fft':
                assert a==0x20017020
                # Record the exact prepared input; FFT itself has a separate decoded verifier.
                calls.append(('fft_input',tuple(get(b+i*2,2) for i in range(frame+padding))))
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0x60000000+i
            r['r0']=result&M
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x4e674','--stop-address=0x4f10c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    candidate=decode((ROOT/'build/gx8002-imcra-prepare/prepare.disassembly.txt').read_text())
    rng=random.Random(0x4e674);cases=0
    for pattern in ("random", "zero", "extrema"):
        for length in (1,2,3,16,255,256,511,512):
            for hop in sorted({0,1,length//2,length}):
                for padding in (0,3):
                    for mutate in (False,True):
                        values=[rng.randrange(-32768,32768) for _ in range(length)]
                        window=[rng.randrange(-32768,32768) for _ in range(length)]
                        if pattern=='zero': values=[0]*length
                        elif pattern=='extrema':
                            values=[(-32768,32767,-1,1)[i%4] for i in range(length)]
                            window=[(-32768,-32768,32767,0)[i%4] for i in range(length)]
                        a=execute(stock,False,values,window,hop,padding,mutate)
                        b=execute(candidate,True,values,window,hop,padding,mutate)
                        assert a==b,(length,hop,padding,mutate)
                        # Independent array-level oracle, including the mutated second-copy hop.
                        history=values[:]
                        history[:length-hop]=values[hop:]
                        refill=max(0,hop-1) if mutate else hop
                        if refill:history[length-refill:]=values[::-1][:refill]
                        prepared=[signed((v*w)>>15,16) for v,w in zip(history,window)]+[0]*padding
                        peak=max(abs(v) for v in prepared)
                        expected_shift=max(-9,peak.bit_length()-15 if peak else -15)
                        expected=tuple((v>>expected_shift if expected_shift>0 else v<<-expected_shift)&0xffff for v in prepared)
                        assert a[1][-1]==('fft_input',expected)
                        assert signed(a[3])==expected_shift
                        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Compares prefix through forward FFT call only; excludes prologue stack/ABI.', 'Memory helpers, peak and shift are explicit models; FFT input is recorded but FFT not executed.', 'Valid bounded positive frame sizes, nonwrapping RAM; includes state mutation after first move and sample shift.', 'No complete processing or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-prepare-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
