# SPDX-License-Identifier: MIT
"""Restricted decoded audio IRQ execution with ordered MMIO and W1C model."""
import itertools,json,re,subprocess
from build_gx8002_audio_irq_candidate import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0xa0a00000
STATE=0x20027330

def execute(code,entry,enable,status,callbacks,seed,read_hook=None,callback_hook=None,setup_hook=None,raw_callback_hook=None,callback_targets=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=entry;saved=None;trace=[];calls=[];read_counts={}
    memory={BASE+o:0x12340000+o for o in (0x124,0x148,0x168,0x128,0x14c,0x16c)};memory.update({BASE+0x100:enable,BASE+0x104:status})
    targets=callback_targets or tuple(0x10220000+4*i for i in range(4));assert len(targets)==4 and len(set(targets))==4
    for i in range(4):memory[STATE+12+4*i]=targets[i] if callbacks&(1<<i) else 0
    if setup_hook:setup_hook(memory)
    for _ in range(2000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6, r15' and saved is None;saved={k:r[k] for k in ('r4','r5','r6','r15')};r['r14']-=16
        elif op=='pop':
            assert r['r14']==initial['r14']-16;r.update(saved);r['r14']+=16
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));assert not calls
            return r['r0'],trace,{a:v for a,v in memory.items() if not 0x2006ff00<=a<0x20070000}
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','lsli','lsr','andi','and','ori','or'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else a>>(b&31) if op=='lsr' else a&b if op in ('and','andi') else a|b)&MASK
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('bez','bnez','br'):
            if op=='br' or (r[p[0]]==0 if op=='bez' else r[p[0]]!=0):nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK;stack=0x2006ff00<=a<0x20070000
            assert a%4==0 and (stack or a in memory),(hex(a),op)
            if op=='ld.w':
                if not stack and read_hook:
                    read_counts[a]=read_counts.get(a,0)+1;read_hook(memory,a,read_counts[a])
                r[reg]=memory[a]
                if not stack:trace.append(('read',a,r[reg]))
            else:
                if not stack:trace.append(('write',a,r[reg]))
                memory[a]=memory[a]&~r[reg] if a==BASE+0x104 else r[reg]
        elif op in ('bsr','jsr'):
            target=int(args,0) if op=='bsr' else r[p[0]]
            if op=='bsr' and target in code:
                calls.append(nxt);r['r15']=nxt;pc=target;continue
            if op=='bsr':
                assert target+(0x1000dfec if entry==0x17e5c else 0)==0x102099cc
                assert r['r1']==0 and r['r2']==12 and r['r0']==r['r14'];trace.append(('memset',12))
                for offset in (0,4,8):memory[r['r0']+offset]=0
            else:
                assert target in targets;kind=targets.index(target)
                event=('callback',kind,r['r0'])
                if kind<2:event+=tuple(memory[r['r1']+i] for i in (0,4,8))
                trace.append(event)
                if raw_callback_hook:raw_callback_hook(memory,kind,r['r0'],r['r1'],r['r14'])
                if callback_hook:callback_hook(memory,kind,r['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
        elif op=='rts':
            assert calls and r['r15']==calls[-1];nxt=calls.pop()
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('IRQ execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';wrapper=out/'padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17e5c','--stop-address=0x180e4',str(wrapper)],text=True));new=decode((out/'audio-irq.disassembly.txt').read_text());cases=0
    values=(0,MASK,*[1<<i for i in (0,1,2,3,4,5,16,17,18,19,20,24)])
    for args in itertools.product(values,values,(0,1,2,4,8,15),(0,91)):
        actual=execute(new,0x10025e48,*args);expected=execute(old,0x17e5c,*args)
        assert actual==expected,(args,actual,expected)
        assert actual[0]==0
        enable,status,callbacks,seed=args;pending=enable&status;events=[];writes=[]
        def event(kind,mask,addresses=()):
            if callbacks&(1<<kind):events.append(('callback',kind,mask,*addresses))
        energy=(pending>>18)&7
        for bit in (18,19,20):
            if pending&(1<<bit):writes.append(1<<bit)
        if energy:event(2,energy)
        record=pending&7
        if record:event(0,record,tuple(0x12340000+i for i in (0x124,0x148,0x168)))
        for bit in (0,1,2):
            if pending&(1<<bit):writes.append(1<<bit)
        update=(pending>>3)&7
        if update:event(1,update,tuple(0x12340000+off if update&(1<<i) else 0 for i,off in enumerate((0x128,0x14c,0x16c))))
        for bit in (3,4,5,16,17):
            if pending&(1<<bit):writes.append(1<<bit)
        event(3,(pending>>16)&3)
        assert [e for e in actual[1] if e[0]=='callback']==events,args
        assert [e[2] for e in actual[1] if e[0]=='write']==writes,args
        cleared=sum(writes)
        assert actual[2][BASE+0x104]==status&~cleared
        cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source ordered MMIO/state reads, W1C writes, callback arguments, memset calls, final memory and callee-saved ABI agree for static register inputs. Independent callback/acknowledgement/final-status oracle also checked. Dynamic status and callback mutations pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-irq-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
