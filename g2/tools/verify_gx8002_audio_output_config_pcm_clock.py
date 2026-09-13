# SPDX-License-Identifier: MIT
"""Qualify the decoded PCM validation prefix; not the full routine."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_config_pcm import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,bits,rate,frequency):
    r={f'r{i}':0 for i in range(32)};r.update(r0=0x20010000,r1=0x20020000);pc=entry;condition=False;trace=[]
    for _ in range(70):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];jump=None
        if op=='push':pass
        elif op in ('pop','rts'):return ('reject',r['r0'],trace)
        elif op in ('mov','movi'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='divu':
            if not r[p[2]]:raise ValueError('Zero rate unqualified')
            r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='mult':r[p[0]]=((r[p[1]]*r[p[2]]) if len(p)==3 else (r[p[0]]*r[p[1]]))&0xffffffff
        elif op=='subu':r[p[0]]=((r[p[1]]-r[p[2]]) if len(p)==3 else (r[p[0]]-r[p[1]]))&0xffffffff
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('ld.w','ld.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();a=r[base]+int(off,0)
            if a==0x20010030:r[reg]=0x20030000
            else:
                values={0x20020005:bits,0x20020000:rate,0x20020008:frequency}
                if a not in values:raise ValueError('Unexpected clock read')
                r[reg]=values[a];trace.append((a-0x20020000,1 if op=='ld.b' else 4,r[reg]))
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups()
            if r[base]+int(off,0)!=0x20030010:raise ValueError('Unexpected clock store')
            return ('accept',r[reg],trace)
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='lrw':
            if int(p[1],0)!=0x1020a9b0:raise ValueError('Diagnostic pointer')
            r[p[0]]=int(p[1],0)
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe2c4 else 0))&0xffffffff
            if target!=0x10206c24 or r['r0']!=0x1020a9b0:raise ValueError('Diagnostic call')
            trace.append(('diagnostic',));r['r0']=123
        else:raise ValueError('Clock opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Clock bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe2c4','--stop-address=0xe3f8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-config-pcm/bits.disassembly.txt').read_text());cases=0
    ratios={128:3,192:7,256:0,384:4,512:1,768:5,1024:2,1536:6}
    for bits,rate,ratio,extra in product((0,8,15,16,17,24,31,32,33,255),(1,8000,16000,48000),range(0,1538),(0,1)):
        frequency=rate*ratio+extra;trace=[(5,1,bits)];mode=None
        if bits in (16,32):
            trace.append((8,4,frequency))
            if frequency:trace.append((0,4,rate))
            if not frequency or frequency%rate:trace.append(('diagnostic',))
            else:mode=ratios.get(frequency//rate)
        wanted=('accept',mode,trace) if mode is not None else ('reject',0xffffffff,trace)
        for code,entry in ((old,0xe2c4),(new,0x10204d38)):
            if execute(code,entry,bits,rate,frequency)!=wanted:raise ValueError(('Clock behavior',entry,bits,rate,frequency))
        cases+=1
    return {'candidate':candidate,'decoded_prefix_cases':cases,'source_admitted':False,'limits':['Checks stop at first settings write on valid input. Remaining MMIO, ABI and nested helper behavior are not qualified. Nonzero frequency with zero rate excluded.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-pcm-clock-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_prefix_cases'])
