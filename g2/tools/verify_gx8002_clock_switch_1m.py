# SPDX-License-Identifier: MIT
"""Decoded 1 MHz policy comparison with adversarial helper boundaries."""
import json,re,random,subprocess,struct
from build_gx8002_clock_switch_1m_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,answers,gate,enable,selectors,gate_runner=None,divider_runner=None,audio_runner=None,pll_runner=None,selector_runner=None,copy_runner=None,lowpower_runner=None):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=entry;condition=False;trace=[]
    memory={0x20027318:gate,0x200268c8:enable};stack=set()
    for _ in range(600):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6, r15';saved={f'r{i}':r[f'r{i}'] for i in (4,5,6,15)};r['r14']-=16
        elif op=='pop':
            r.update(saved);r['r14']+=16;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace,memory[0x20027318],memory[0x200268c8]
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='lsl':r[p[0]]=(r[p[0]]<<(r[p[1]]&31))&0xffffffff
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            assert address in (0x20027318,0x200268c8)
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0);result=0xdead1234
            if target==0x10025738:
                assert r['r1']==0x10025cd0 and r['r2']==16 and r['r0']==r['r14'];assert selectors==(28,0,18,1)
                copied=copy_runner(r['r0'],r['r1'],r['r2']) if copy_runner else selectors
                for i,v in enumerate(copied):memory[r['r0']+i*4]=v;stack.add(r['r0']+i*4)
            elif target==0x10024bcc:
                assert r['r0'] in stack and r['r0']+4 in stack;trace.append(('source',memory[r['r0']],memory[r['r0']+4]))
                if selector_runner:selector_runner(memory[r['r0']],memory[r['r0']+4])
            elif target==0x1002599c:
                trace.append(('lowpower',))
                if lowpower_runner:lowpower_runner()
            elif target==0x10025180:result=gate_runner(r['r0']) if gate_runner else answers[r['r0']];trace.append(('gate',r['r0'],result))
            elif target==0x10025a00:
                trace.append(('audio_dividers',))
                if audio_runner:audio_runner()
            elif target==0x10024df8:
                trace.append(('divider',r['r0'],r['r1']))
                if divider_runner:divider_runner(r['r0'],r['r1'])
            elif target==0x10025060:
                assert r['r0']==0x200268c8;trace.append(('pll',memory[r['r0']]))
                if pll_runner:pll_runner(memory[r['r0']])
            else:raise ValueError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')


def expected(answers,gate,enable):
    trace=[('source',28,0),('source',18,1),('lowpower',)]
    for module in range(11,26):
        value=answers[module];trace.append(('gate',module,value))
        if value!=0xffffffff:
            trace.append(('read',0x20027318,gate));gate|=(value&1)<<module;trace.append(('write',0x20027318,gate))
    trace.extend([('audio_dividers',),('divider',10,0),('read',0x200268c8,enable)])
    if enable==1:trace.extend([('write',0x200268c8,0),('pll',0),('write',0x200268c8,1)])
    return trace,gate,enable


def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17a28','--stop-address=0x17a9c',str(path)],text=True));new=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text())
    selectors=struct.unpack('<4I',IMAGE.read_bytes()[0x17ce4:0x17cf4]);rng=random.Random(412);cases=0
    for enable in (0,1,2,0xffffffff):
        for gate in (0,0xffffffff,0xaaaaaaaa,0x55555555):
            for pattern in range(40):
                answers={m:((0,1,2,0xffffffff)[pattern] if pattern<4 else rng.choice((0,1,2,0xffffffff,rng.getrandbits(32)))) for m in range(11,26)}
                a=execute(old,0x17a28,answers,gate,enable,selectors);b=execute(new,0x10025a14,answers,gate,enable,selectors)
                assert a==b==expected(answers,gate,enable);cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source outer policy and integer ABI agree with independent trace oracle. Helpers modeled, memcpy initializer marshalled; nested helpers and physical timing remain unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
