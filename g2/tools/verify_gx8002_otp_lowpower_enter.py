# SPDX-License-Identifier: MIT
"""Decoded low-power caller trace equivalence; peripheral effects modeled."""
import json,re,subprocess
from itertools import product
from build_gx8002_otp_lowpower_enter_candidate import build,ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,configuration,status,values,seed,otp_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x20050000;initial=r.copy();saved=None;local={};events=[];pc=entry;carry=None
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            names=('r4','r5','r6','r15') if entry==0x168e0 else ('r4','r15')
            assert args==('r4-r6, r15' if entry==0x168e0 else 'r4, r15')
            assert saved is None;saved={n:r[n] for n in names};r['r14']-=4*len(names)
        elif op=='pop':
            assert r['r14']==initial['r14']-4*len(saved)
            r.update(saved);r['r14']=initial['r14']
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return events
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli','rotli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)))&MASK
        elif op in ('ori','andni','andn'):
            a=r[p[1]];b=r[p[2]] if op=='andn' else int(p[2],0)
            r[p[0]]=(a|b if op=='ori' else a&~b)&MASK
        elif op in ('nor','and'):
            a,b=r[p[0]],r[p[1]];r[p[0]]=(~(a|b) if op=='nor' else a&b)&MASK
        elif op=='ins':
            hi,lo=map(int,p[2:]);mask=((1<<(hi-lo+1))-1)<<lo
            r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            if address==r['r14']:
                if op=='st.w':local[address]=r[reg]
                else:r[reg]=local[address]
            elif op=='ld.w':
                assert address in values;r[reg]=values[address];events.append(('read',address,r[reg]))
            else:
                assert address in (0xa0000024,0xa0000028,0xa0000038,0xa0000034,0xe000f004,0xa0000000)
                events.append(('write',address,r[reg]))
        elif op=='cmpnei':carry=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf','br'):
            assert carry is not None or op=='br'
            if op=='br' or carry==(op=='bt'):nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry==0x168e0 else 0)
            if target==0x10025d04:
                assert r['r0']==r['r14'] and local[r['r0']]==0
                returned,selected=(status,configuration) if otp_hook is None else otp_hook()
                local[r['r0']]=selected;events.append(('otp',))
            else:assert target==0x10025a14;events.append(('clock',));returned=0x76543210
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=returned
        elif op in ('sync','doze'):events.append((op,))
        else:raise ValueError((op,args))
        pc=nxt
    raise ValueError('execution bound')

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x168e0','--stop-address=0x16954',str(path)],text=True));new=decode((ROOT/'build/gx8002-board/otp-lowpower-enter.disassembly.txt').read_text());cases=0
    for configuration,status,seed,value in product((0,0x8002,0x8003a,MASK),(0,5,0x80000000,MASK),(0,91),(0,MASK,0xaaaaaaaa,0x55555555,*[1<<i for i in range(32)])):
        values={0xa0000024:value,0xa0000028:value^MASK,0xa0000038:value};wanted=[('otp',)]
        if configuration==0x8002:
            for address in (0xa0000024,0xa0000028,0xa0000038):
                original=values[address];wanted.append(('read',address,original))
                # Model the stock field assignments individually.
                result=original&~0x10 if address==0xa0000038 else (original&~(1<<8)&~(15<<14))|(1<<13)|(1<<14)
                if address==0xa0000024:result|=1<<11
                wanted.append(('write',address,result))
            wanted += [('write',0xa0000034,15),('clock',),('sync',),('sync',),('write',0xe000f004,5),('sync',),('sync',),('write',0xa0000000,1),('doze',)]
        assert execute(old,0x168e0,configuration,status,values,seed)==execute(new,0x100248cc,configuration,status,values,seed)==wanted
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded register IO, OTP output selection, ignored OTP status, barrier/doze order and ABI checked. OTP/clock effects modeled; doze treated as returning after wake. Physical power behavior unqualified; candidate fits current slot but remains unregistered.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-otp-lowpower-enter-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
