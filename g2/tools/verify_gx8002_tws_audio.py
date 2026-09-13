# SPDX-License-Identifier: MIT
"""Decoded TWS audio callback comparison with independent state/call oracle."""
import itertools,json,re,subprocess
from build_gx8002_tws_audio_candidate import build,ROOT,sha,IMAGE,IMAGE_SHA,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
MASK=0xffffffff
CTX=0x20050000
HEADER=0x20051000
STATE=0x2002e6ec

def execute(code,entry,bindings,index,mics,enabled,delayed,last,standby,countdown,seed,hook=None,standby_hook=None,mic_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=index&MASK,r14=0x20070000);initial=r.copy();saved=None;pc=entry;condition=False;events=[];memory={}
    for base,length in ((CTX,32),(HEADER,112),(STATE,88)):
        memory.update({base+i:0xa5 for i in range(length)})
    for a,v in ((CTX,HEADER),(CTX+8,123),(HEADER+4,enabled),(HEADER+8,mics),(HEADER+36,2),(HEADER+48,26),(STATE+76,standby),(STATE+80,countdown),(STATE+84,last)):word(memory,a,v)
    names={v:k for k,v in bindings.items()}
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args in ('r4-r6, r15','r4-r7, r15') and saved is None
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,7 if entry==0x183f0 else 8),15)};r['r14']-=4*len(saved)
        elif op=='pop':
            assert r['r14']==initial['r14']-4*len(saved);r.update(saved);r['r14']+=4*len(saved)
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
        elif op in ('br','bt','bf','bez','bnez','blz'):
            take=op=='blz' and signed(r[p[0]])<0 or op=='br' or op=='bt' and condition or op=='bf' and not condition or op=='bez' and r[p[0]]==0 or op=='bnez' and r[p[0]]!=0
            if take:nxt=int(p[-1],0)
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry==0x183f0 else 0);name=names[target];value=0;event=(name,)
            if name=='LvpGetContext':
                assert r['r0']==index&MASK;word(memory,r['r1'],CTX);word(memory,r['r2'],32);event=(name,index&MASK)
            elif name=='LvpAudioInGetDelayedFFTVad':value=delayed
            elif name=='LvpGetMicFrame':
                assert r['r0']==CTX and r['r2']==0;event=(name,r['r1']);value=mic_hook(memory,r['r1'],r['r2']) if mic_hook else 0x20052000
            elif name=='LvpAuidoInQueryEnvNoise':
                assert r['r0']==CTX;memory[CTX+14]=(memory[CTX+14]&~7)|3
            elif name=='LvpGetContextHeader':value=HEADER
            elif name=='open_cfw_gx8002_tws_standby_loop':
                if standby_hook:standby_hook(memory)
                elif word(memory,STATE+76)==2:
                    n=(word(memory,STATE+80)-1)&MASK;word(memory,STATE+80,n)
                    if not n:word(memory,STATE+76,4)
            elif name=='LvpKwsRun':assert r['r0']==CTX
            elif name=='printf':
                assert r['r0']==0x1020b250;event=(name,r['r1'],r['r2'],r['r3'],word(memory,r['r14']))
            elif name=='LvpTriggerAppEvent':event=(name,word(memory,r['r0']),word(memory,r['r0']+4))
            else:raise ValueError(name)
            events.append(event)
            if hook:hook(name,memory)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value&MASK
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('TWS audio execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    analysis=Elf32((out/'padmux-get-stock.elf').read_bytes(),'stock analysis');section=next(s for s in analysis.sections if s['name']=='.data');assert analysis.contents(section)==stock
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x183f0','--stop-address=0x184e8',str(out/'padmux-get-stock.elf')],text=True));new=decode((out/'tws-audio.disassembly.txt').read_text());cases=0
    for args in itertools.product((-1,0,1,13,14,15,30,0x7fffffff),(0,1,2),(0,1),(0,1,7),(0,1,7),(2,4),(0,1,50),(0,91)):
        actual=execute(new,0x100263dc,evidence['bindings'],*args)
        assert execute(old,0x183f0,evidence['bindings'],*args)==actual,args
        index,mics,enabled,delayed,last,standby,countdown,seed=args
        result,memory,events=actual;expected=[];assert result==0
        if index>=0:
            vad=1 if not enabled or index<=13 else delayed&7
            expected=[('LvpGetContext',index),('LvpAudioInGetDelayedFFTVad',)]+[('LvpGetMicFrame',i) for i in range(mics)]+[('LvpAuidoInQueryEnvNoise',)]
            if enabled:expected.append(('LvpGetContextHeader',))
            expected += [('open_cfw_gx8002_tws_standby_loop',),('LvpKwsRun',)]
            if index%15==0 or last!=vad:expected.append(('printf',index,vad,3,0))
            expected.append(('LvpTriggerAppEvent',91,index))
            if standby==2:
                countdown=(countdown-1)&MASK
                if not countdown:standby=4
            if vad:standby,countdown=2,50
            assert word(memory,CTX+8)==index and memory[CTX+12]==((0xa5&~0xc7)|vad)
            assert word(memory,STATE+84)==vad
        else:assert word(memory,CTX+8)==123 and word(memory,STATE+84)==last
        assert (word(memory,STATE+76),word(memory,STATE+80))==(standby,countdown)
        assert events==expected,args
        cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source return, final byte memory, ordered helper calls and callee-saved ABI agree; independent state/event oracle. Helpers modeled; concurrent mutation, integration and state ownership pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-audio-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
