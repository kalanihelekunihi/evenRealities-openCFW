# SPDX-License-Identifier: MIT
"""Decode VAD parameter transitions up to state acquisition."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_query_vad import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x101f6a74;LEVEL=0x2002dfa4;MASK=0xffffffff


def execute(code,entry,noise,level,padding,state=None,mutation=None):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;pc=entry;condition=False;events=[];initial=r.copy();saved=None;memory={LEVEL+i:b for i,b in enumerate(level.to_bytes(4,'little'))}
    for _ in range(160):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+w
        if op=='push':
            if args not in ('r15','r4-r5, r15'):raise ValueError('Frame')
            saved={v:r[v] for v in (('r15',) if args=='r15' else ('r4','r5','r15'))}
            r['r14']-=len(saved)*4
        elif op=='pop':
            if saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=len(saved)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0']
        elif op in ('mov','movi','lrw','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','lsli'):
            a,b=(r[p[0]],int(p[1],0)) if len(p)==2 else (r[p[1]],int(p[2],0))
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
            if p[0]=='r14':
                for i in range(20):memory[r['r14']+i]=padding
        elif op in ('addu','subu','mult','and','lsl','lsr'):
            a,b=(r[p[0]],r[p[1]]) if len(p)==2 else (r[p[1]],r[p[2]])
            r[p[0]]=(a+b if op=='addu' else a-b if op=='subu' else a*b if op=='mult' else a&b if op=='and' else a>>(b&31) if op=='lsr' else a<<(b&31))&MASK
        elif op in ('divs','divu'):r[p[0]]=r[p[1]]//r[p[2]] # Operands here are nonnegative16-bit index+94 and95.
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('cmphsi','cmplti'):condition=(r[p[0]]>=int(p[1],0)) if op=='cmphsi' else (r[p[0]]<int(p[1],0))
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op in ('ld.w','ld.h','st.w','st.h','st.b'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(offset,0))&MASK;n={'st.b':1,'st.h':2,'ld.h':2}.get(op,4)
            if address%n or any(address+i not in memory for i in range(n)):raise ValueError('Memory bounds')
            if op in ('ld.w','ld.h'):r[reg]=int.from_bytes(bytes(memory[address+i] for i in range(n)),'little')
            else:
                for i,b in enumerate((r[reg]&((1<<(8*n))-1)).to_bytes(n,'little')):memory[address+i]=b
                if address==LEVEL:events.append(('level',r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(BASE if entry==0x10990 else 0))&MASK;offset=target-BASE
            if offset==0xdd08:
                if state is None:return events,int.from_bytes(bytes(memory[LEVEL+i] for i in range(4)),'little')
                address=r['r0']
                if address!=r['r14']+4:raise ValueError('State destination')
                data=b''.join(v.to_bytes(4,'little') for v in state[:3])+state[3].to_bytes(2,'little')
                for i,b in enumerate(data):memory[address+i]=b
                result=0
            elif offset==0xdd38:events.append(('noise',));result=noise
            else:
                counts={0x101b0:2,0xdbbc:2,0xdbf0:2,0xdc24:2,0xdc64:2,0xdc98:1,0xdcb8:2,0xdb80:1}
                if offset not in counts:raise ValueError('Target')
                values=tuple(r[f'r{i}'] for i in range(counts[offset]))
                if offset==0xdb80:values=(values[0]&0xffffff,) # Fourth ABI byte ignored by decoded consumer.
                events.append((offset,values));result=0
            if mutation:
                current=int.from_bytes(bytes(memory[LEVEL+i] for i in range(4)),'little')
                changed=mutation(offset,current)
                for i,b in enumerate(changed.to_bytes(4,'little')):memory[LEVEL+i]=b
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=result
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10990','--stop-address=0x10b54',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-query-vad/index.disassembly.txt').read_text());cases=0
    for noise,level,padding in product((0,1,3145727,3145728,3145729,6291455,6291456,6291457,20971519,20971520,20971521,0xffffffff),(0,1,2,3,4,5,0xffffffff),(0,255)):
        next_level=4 if noise<3145728 else 3 if noise<6291456 else 2 if noise<=20971520 else 1
        events=[('noise',)]
        if level!=next_level:
            message={4:0x1020ae14,3:0x1020ae2f,2:0x1020ae4a,1:0x1020ae65}[next_level]
            events += [(0x101b0,(message,noise)),('level',next_level),(0xdbbc,(1024,3840)),(0xdbf0,(1229,1536)),(0xdc24,(1229,8192)),(0xdc64,(1843,819)),(0xdc98,(2560,)),(0xdcb8,(0x0106028f,0x00210083)),(0xdb80,(0x101,))]
        for code,entry in ((old,0x10990),(new,0x10207404)):
            if execute(code,entry,noise,level,padding)!=(events,next_level):raise ValueError(('Transition',noise,level,padding))
        cases+=1
    return {'candidate':candidate,'transition_cases':cases,'source_admitted':False,'limits':['Prefix through state acquisition only. Independent threshold/call oracle; driver bodies modeled. Final VAD selection and ABI restoration pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-vad-query-transitions.json').write_text(json.dumps(report,indent=2)+'\n');print(report['transition_cases'])
