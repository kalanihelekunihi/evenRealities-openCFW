# SPDX-License-Identifier: MIT
"""Qualify arithmetic PGA encoding against decoded stock table lookup."""
import json,re,random,subprocess
from build_gx8002_audio_pga_gain import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,gain,word,control,table):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=gain;initial=r.copy()
    memory={0xa0a001a4:word,0xa0a001a0:control};trace=[];pc=entry;condition=False
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Gain ABI')
            return r['r0'],trace,memory
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('subi','lsli'):
            value=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0);r[p[0]]=(value-n if op=='subi' else value<<n)&0xffffffff
        elif op in ('divu','mult','subu','addu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]]
            r[p[0]]={'divu':lambda:a//b,'mult':lambda:a*b,'subu':lambda:a-b,'addu':lambda:a+b}[op]()&0xffffffff
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='ldr.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args)
            if not m:raise ValueError('Gain table operand')
            dest,base,index=m.groups();address=r[base]+r[index]
            if entry!=0xd860 or not 0x1020a8ee<=address<0x1020a8f3:raise ValueError('Unexpected table access')
            r[dest]=table[address-0x1020a8ee]
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Gain memory operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if address not in memory:raise ValueError('Gain unexpected address')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        else:raise ValueError('Gain instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Gain execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    stock=elf.contents(next(s for s in elf.sections if s['name']=='.data'))
    if sha(stock)!=IMAGE_SHA:raise ValueError('Gain stock wrapper')
    table=stock[0x13e7a:0x13e7f]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd860','--stop-address=0xd8ac',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-pga-gain/gain.disassembly.txt').read_text())
    rng=random.Random(804);gains=set(range(1024));gains.update(range(0xffffff00,0x100000000));gains.update(rng.getrandbits(32) for _ in range(1024));cases=0
    for gain in sorted(gains):
        q,remainder=divmod(gain,6)
        # Independent piecewise mapping of the five exceptional bands.
        encoded=(q+remainder+{4:5,5:10,6:15,7:20,8:25}.get(q,0))&63
        for word,control in ((0,0),(0xffffffff,0xffffffff),(0xa5a5a5a5,0x12345678)):
            value=(word&~63)|encoded;enabled=control|0x80000000
            wanted=(0,[('read',0xa0a001a4,word),('write',0xa0a001a4,value),('read',0xa0a001a0,control),('write',0xa0a001a0,enabled)],{0xa0a001a4:value,0xa0a001a0:enabled})
            if execute(old,0xd860,gain,word,control,table)!=wanted or execute(new,0x102042d4,gain,word,control,table)!=wanted:raise ValueError('Gain oracle '+str(gain))
            cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Stock table used only as verification evidence; compiled source computes correction arithmetically. Low gain range, unsigned extremes and seeded random words checked; not exhaustive over uint32. Physical gain response unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-pga-gain-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Gain cases:',r['decoded_cases'])
