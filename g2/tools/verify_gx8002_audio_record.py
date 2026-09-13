# SPDX-License-Identifier: MIT
"""Restricted decoded stock/source audio frame callback comparison."""
import json,re,subprocess,itertools
from build_gx8002_audio_record_candidate import build,ROOT,sha,IMAGE,IMAGE_SHA,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
MASK=0xffffffff
CTRL=0x2002ecb0
SDC=0x20050000
HEADER=0x20027b60

def execute(code,entry,bindings,channel,read,write,flags,vad,invalid,index,seed,record_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=channel,r1=SDC,r14=0x20070000);initial=r.copy();saved=None;pc=entry;condition=False;events=[];memory={}
    for base,length in ((CTRL,20),(SDC,12),(HEADER,112),(0x2002dfa0,12)):
        memory.update({base+i:0 for i in range(length)})
    for a,v in ((CTRL,read),(CTRL+4,write),(CTRL+16,flags),(SDC+8,index*80),(HEADER+36,1),(HEADER+108,40),(0x2002dfa0,0x10210000),(0x2002dfa8,invalid)):word(memory,a,v)
    names={v:k for k,v in bindings.items()}
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r11, r15, r16-r17' and saved is None
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=44
        elif op=='pop':
            assert r['r14']==initial['r14']-44;r.update(saved);r['r14']+=44
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],{a:v for a,v in memory.items() if not 0x2006ff00<=a<0x20070000},events
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','subu','mult','lsli','andi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a*b if op=='mult' else a<<b if op=='lsli' else a&b)&MASK
        elif op in ('divu','divs'):
            a,b=r[p[1]],r[p[2]]
            if op=='divs':a,b=signed(a),signed(b)
            assert b;r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='ins':
            hi,lo=map(int,p[2:]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=word(memory,a)
            elif op=='ld.b':r[reg]=memory[a]
            elif op=='st.w':word(memory,a,r[reg])
            else:memory[a]=r[reg]&255
        elif op in ('cmphs','cmpne','cmplti'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b if op=='cmpne' else signed(a)<b
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf','bez','bnez'):
            take=op=='br' or op=='bt' and condition or op=='bf' and not condition or op=='bez' and r[p[0]]==0 or op=='bnez' and r[p[0]]!=0
            if take:nxt=int(p[-1],0)
        elif op in ('bsr','jsr'):
            if op=='jsr':
                assert r[p[0]]==0x10210000 and r['r1']==SDC+8
                events.append(('record',r['r0'],r['r1']));value=seed
                if record_hook:value=record_hook(memory,r['r0'],r['r1'])
            else:
                target=int(args,0)+(0x1000dfec if entry==0x18228 else 0);name=names[target];events.append((name,))
                if name=='LvpAudioInQueryFFTVad':assert r['r0']==SDC+8;value=vad
                else:value={'LvpGetContextHeader':HEADER,'LvpGetLogfbankFrameNumPerChannel':13,'LvpGetPcmFrameNumPerContext':1,'LvpGetContextNum':3,'LvpGetContextGap':1}[name]
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value&MASK
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('audio record execution bound')


def expected_state(channel,read,write,flags,vad,invalid,index):
    start=0;delayed=0;records=[]
    if channel&4:
        flags=(flags&~15)|(vad&15)
        if flags&240:
            write=read=(index+2)&MASK;start=index;flags=(flags&~255)|1;delayed=1
        while write%13!=index:
            if write>3 and ((write-read)&MASK)>=2:break
            if vad or write<=13:delayed=1;invalid=0
            else:
                invalid=(invalid+1)&MASK
                delayed=int((invalid if invalid<0x80000000 else invalid-0x100000000)<25)
            records.append(('record',write,SDC+8));write=(write+1)&MASK
    return (read,write,start,delayed,flags,invalid),records

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    analysis=Elf32((out/'padmux-get-stock.elf').read_bytes(),'stock analysis');section=next(s for s in analysis.sections if s['name']=='.data');assert analysis.contents(section)==stock
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x18228','--stop-address=0x18328',str(out/'padmux-get-stock.elf')],text=True));new=decode((out/'audio-record.disassembly.txt').read_text());cases=0
    for channel,indices,flags,vad,invalid,index,seed in itertools.product((0,4,5),((0,0),(2,3),(5,6),(0,5),(14,14),(0xffffffff,0)),(0,0x10,0xf3),(0,1),(0,23,24,25),(0,3,12),(0,91)):
        args=(channel,*indices,flags,vad,invalid,index,seed)
        actual=execute(new,0x10026214,evidence['bindings'],*args)
        assert execute(old,0x18228,evidence['bindings'],*args)==actual,args
        state,records=expected_state(*args[:-1]);memory=actual[1]
        assert tuple(word(memory,a) for a in (CTRL,CTRL+4,CTRL+8,CTRL+12,CTRL+16,0x2002dfa8))==state,args
        assert [e for e in actual[2] if e[0]=='record']==records,args
        cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source return values, final memory and ordered helper/callback calls agree; independent state and emitted-frame oracle checked. Helper bodies modeled; no concurrent mutation, memory-access ordering oracle or physical execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-record-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
