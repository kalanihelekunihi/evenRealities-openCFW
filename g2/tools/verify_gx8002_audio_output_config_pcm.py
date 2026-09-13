# SPDX-License-Identifier: MIT
"""Qualify full decoded PCM effects with modeled helper calls."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_config_pcm import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,config,seed,mutation,helper_hook=None):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=0x20010000,r1=0x20020000,r14=0x20070000);saved=r.copy();pc=entry;condition=False;trace=[];stack={}
    state=bytearray([0xa5]*64);state[48:52]=(0x20030000).to_bytes(4,'little');settings=bytearray([0x5a]*96);word=seed
    for _ in range(150):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];jump=None
        if op=='push':
            if args!='r4, r15':raise ValueError('PCM frame')
            r['r14']-=8;stack[r['r14']]=r['r4'];stack[r['r14']+4]=r['r15']
        elif op=='pop':
            if args!='r4, r15':raise ValueError('PCM restore')
            r['r4']=stack[r['r14']];r['r15']=stack[r['r14']+4];r['r14']+=8
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('PCM ABI')
            return r['r0'],trace,word,bytes(state),bytes(settings)
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
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
        elif op in ('subi','addi'):
            base=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(base+(-1 if op=='subi' else 1)*int(p[-1],0))&0xffffffff
        elif op in ('and','or'):r[p[0]]=r[p[0]]&r[p[1]] if op=='and' else r[p[0]]|r[p[1]]
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='bclri':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]])&~(1<<int(p[-1],0))
        elif op in ('mvc','mvcv'):r[p[0]]=int(condition if op=='mvc' else not condition)
        elif op in ('lsri','lsli'):r[p[0]]=((r[p[1]]>>int(p[2],0)) if op=='lsri' else (r[p[1]]<<int(p[2],0)))&0xffffffff
        elif op in ('ld.w','ld.b','st.w','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();a=r[base]+int(off,0);size=4 if op.endswith('w') else 1
            if a==0xa0b80000:
                if size!=4:raise ValueError('PCM MMIO width')
                if op.startswith('ld'):r[reg]=word;trace.append(('read',a,word))
                else:word=r[reg];trace.append(('write',a,word))
            else:
                if 0x20010000<=a<=0x20010040-size:memory=state;offset=a-0x20010000
                elif 0x20020000<=a<=0x2002000c-size:memory=config;offset=a-0x20020000
                elif 0x20030000<=a<=0x20030060-size:memory=settings;offset=a-0x20030000
                else:raise ValueError('PCM RAM address')
                if op.startswith('ld'):r[reg]=int.from_bytes(memory[offset:offset+size],'little');trace.append(('ram_read',a,size,r[reg]))
                else:
                    if memory is config:raise ValueError('Config write')
                    value=r[reg]&((1<<(size*8))-1);memory[offset:offset+size]=value.to_bytes(size,'little');trace.append(('ram_write',a,size,value))
        elif op=='lrw':
            if int(p[1],0)!=0x1020a9b0:raise ValueError('Diagnostic pointer')
            r[p[0]]=int(p[1],0)
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe2c4 else 0))&0xffffffff
            if target==0x10206c24:
                if r['r0']!=0x1020a9b0:raise ValueError('Diagnostic pointer')
                trace.append(('diagnostic',))
            elif target in (0x10204ab0,0x102049e8):
                trace.append(('helper',target,r['r0'],r['r1']))
                if helper_hook:trace.extend(helper_hook(target,r['r0'],r['r1'],bytes(settings)))
                if target==0x10204ab0 and mutation:state[48:52]=(0x20030010).to_bytes(4,'little')
            elif target==0x10204b5c:
                trace.append(('helper',target))
                if helper_hook:trace.extend(helper_hook(target,None,None,bytes(settings)))
            else:raise ValueError('PCM call target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Clock opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Clock bound')

def oracle(config,seed,mutation):
    state=bytearray([0xa5]*64);state[48:52]=(0x20030000).to_bytes(4,'little');settings=bytearray([0x5a]*96);trace=[];word=seed
    def read_config(offset,size):
        value=int.from_bytes(config[offset:offset+size],'little');trace.append(('ram_read',0x20020000+offset,size,value));return value
    bits=read_config(5,1);mode=None
    if bits in (16,32):
        frequency=read_config(8,4);rate=read_config(0,4) if frequency else 1
        if not frequency or frequency%rate:trace.append(('diagnostic',))
        else:mode={128:3,192:7,256:0,384:4,512:1,768:5,1024:2,1536:6}.get(frequency//rate)
    if mode is None:return 0xffffffff,trace,word,bytes(state),bytes(settings)
    trace.extend((('ram_read',0x20010030,4,0x20030000),('ram_write',0x20030010,4,mode),('ram_write',0x20010019,1,bits//8)))
    settings[16:20]=mode.to_bytes(4,'little');state[25]=bits//8;channels=read_config(4,1)
    for mask,value in ((15,8 if bits==16 else 0),(64,64 if channels!=1 else 0)):
        trace.append(('read',0xa0b80000,word));word=(word&~mask)|value;trace.append(('write',0xa0b80000,word))
    trace.append(('read',0xa0b80000,word));interlace=read_config(6,1);word=(word&~128)|(128 if interlace else 0);trace.append(('write',0xa0b80000,word))
    trace.append(('read',0xa0b80000,word));endian=read_config(7,1);trace.append(('ram_read',0x20010030,4,0x20030000));word=(word&~48)|(16 if endian else 0);trace.append(('write',0xa0b80000,word))
    trace.append(('helper',0x10204ab0,0xa0b00000,0x20030008))
    pointer=0x20030010 if mutation else 0x20030000;state[48:52]=pointer.to_bytes(4,'little')
    trace.extend((('ram_read',0x20010030,4,pointer),('helper',0x102049e8,0xa0b00000,pointer+48),('helper',0x10204b5c)))
    return 0,trace,word,bytes(state),bytes(settings)

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe2c4','--stop-address=0xe3f8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-config-pcm/bits.disassembly.txt').read_text());cases=0
    for bits,ratio,channels,interlace,endian,seed,mutation in product((16,32),(128,192,256,384,512,768,1024,1536),(0,1,2,255),(0,1,255),(0,1,255),(0,0xffffffff,0xa5a5a5a5),(False,True)):
        config=(16000).to_bytes(4,'little')+bytes((channels,bits,interlace,endian))+(16000*ratio).to_bytes(4,'little');wanted=oracle(config,seed,mutation)
        for code,entry in ((old,0xe2c4),(new,0x10204d38)):
            result=execute(code,entry,config,seed,mutation)
            if result!=wanted:raise ValueError(('PCM effects',hex(entry),bits,ratio,channels,interlace,endian,result,wanted))
        cases+=1
    rejects=0
    for bits,rate,frequency in product((0,16,24,32,255),(1,16000),(0,1,15999,16000,0xffffffff)):
        config=rate.to_bytes(4,'little')+bytes((2,bits,1,1))+frequency.to_bytes(4,'little');wanted=oracle(config,0,False)
        for code,entry in ((old,0xe2c4),(new,0x10204d38)):
            if execute(code,entry,config,0,False)!=wanted:raise ValueError('PCM rejection effects')
        rejects+=1
    return {'candidate':candidate,'decoded_complete_cases':cases,'additional_validation_cases':rejects,'source_admitted':False,'hardware_qualified':False,'limits':['Valid disjoint handle/settings/config memory. Helper bodies are modeled with caller clobbers and optional settings-pointer mutation; nested hardware effects are not qualified here. Nonzero frequency with zero sample_rate excluded.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-pcm-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_complete_cases'],r['additional_validation_cases'])
