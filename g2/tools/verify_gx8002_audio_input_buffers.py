# SPDX-License-Identifier: MIT
"""Decode audio-input buffer selection with returning helper clobbers."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_buffers import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x101f6a74
TARGETS={0x10404:'mic_size',0x1051c:'mic_count',0x1041c:'log_size',0x103f8:'mic_addr',0x10410:'log_addr',0xc590:'board'}


def execute(code,entry,channel,values,seed,nested=None):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)};r.update(r0=channel,r14=0x20070000);initial=r.copy();pc=entry;saved=None;condition=False;calls=[]
    for _ in range(50):
        op,args,w=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+w
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],calls
        elif op in ('movi','mov'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[1]]-int(p[2],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op=='divu':
            if not r[p[2]]:raise ValueError('Zero divisor outside C contract')
            r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='bsr':
            target=int(args,0)-(BASE if entry>BASE else 0)
            if target not in TARGETS:raise ValueError('Call target')
            name=TARGETS[target];calls.append(name)
            value=nested(name,seed) if nested else values[name]
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xab000000+i+seed)&0xffffffff
            r['r0']=value
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x105b0','--stop-address=0x105fc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-input-buffers/buffers.disassembly.txt').read_text());cases=0
    boundaries=(0,1,2,3840,7680,0x7fffffff,0x80000000,0xffffffff)
    for channel,mic_size,mic_count,log_size in product((*range(256),0x7fffffff,0x80000000,0xffffffff),boundaries,(1,2,3,0x7fffffff,0x80000000,0xffffffff),boundaries):
        values=dict(mic_size=mic_size,mic_count=mic_count,log_size=log_size,mic_addr=mic_size,log_addr=log_size,board=0xffffffff)
        expected_size=((mic_size//mic_count*2)&0xffffffff,['mic_size','mic_count']) if channel==2 else (log_size,['log_size']) if channel==4 else (0,[])
        expected_addr=(mic_size,['board','mic_addr']) if channel in (1,2) else (log_size,['board','log_addr']) if channel==4 else (0,['board'])
        for code,base in ((old,0),(new,BASE)):
            if execute(code,0x105b0+base,channel,values,mic_size^log_size)!=expected_size:raise ValueError('Size selector')
            if execute(code,0x105d8+base,channel,values,mic_size^log_size)!=expected_addr:raise ValueError('Address selector')
        cases+=1
    from verify_gx8002_buffer_accessors import verify as verify_accessors,execute as getter
    from verify_gx8002_buffer_metadata import verify as verify_metadata
    accessor_evidence=verify_accessors();metadata_evidence=verify_metadata()
    source_getters=decode((ROOT/'build/gx8002-buffer-accessors/accessors.disassembly.txt').read_text())
    source_getters.update(decode((ROOT/'build/gx8002-buffer-metadata/metadata.disassembly.txt').read_text()))
    stock_getters=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x103f8','--stop-address=0x10528',str(wrapper)],text=True))
    addresses={name:offset for offset,name in TARGETS.items()}
    fields=dict(mic_size=84,mic_count=8,log_size=116,mic_addr=80,log_addr=112)
    nested_cases=0
    for channel,size,count in product((0,1,2,3,4,0xffffffff),boundaries,(1,2,3,0xffffffff)):
        values=dict(mic_size=size,mic_count=count,log_size=3840,mic_addr=0x20030410,log_addr=0x20032210,board=0x20026d00)
        memory={0x20027b60+offset+i:b for name,offset in fields.items() for i,b in enumerate(values[name].to_bytes(4,'little'))}
        for helpers,helper_base in ((stock_getters,0),(source_getters,BASE)):
            def nested(name,seed):
                if name=='board':return values[name] # Board helper still modeled.
                result,reads=getter(helpers,addresses[name]+helper_base,memory,seed)
                if result!=values[name] or reads!=[0x20027b60+fields[name]]:raise ValueError('Nested getter')
                return result
            for code,base in ((old,0),(new,BASE)):
                for offset in (0x105b0,0x105d8):
                    if execute(code,offset+base,channel,values,size,nested)!=execute(code,offset+base,channel,values,size):raise ValueError('Nested selector')
                    nested_cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'nested_getter_cases':nested_cases,
            'getter_evidence':{'accessors':accessor_evidence,'metadata':metadata_evidence},'source_admitted':False,
            'limits':['Decoded nested stock/source header getters; board getter modeled. Nonzero mic-channel count required on channel2. Physical concurrency and timing unqualified.']}



if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-buffers-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
