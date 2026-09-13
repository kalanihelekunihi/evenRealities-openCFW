# SPDX-License-Identifier: MIT
"""Qualify decoded microphone-frame arithmetic and mapped memory accesses."""
import json,re,subprocess,shutil
from itertools import product
from build_gx8002_mic_frame import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff


def execute(code,entry,memory,channel,frame,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=0x20050000,r1=channel,r2=frame);initial=r.copy();pc=entry;reads=[]
    for _ in range(40):
        op,args,w=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='ld.w':
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(offset,0))&MASK
            if address%4 or any(address+i not in memory for i in range(4)):raise ValueError('Unmapped read')
            r[reg]=int.from_bytes(bytes(memory[address+i] for i in range(4)),'little');reads.append(address)
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op in ('mult','addu','subu'):
            a,b=(r[p[0]],r[p[1]]) if len(p)==2 else (r[p[1]],r[p[2]])
            r[p[0]]=(a*b if op=='mult' else a+b if op=='addu' else a-b)&MASK
        elif op=='divu':
            if r[p[2]]==0:raise ValueError('Zero divisor outside C contract')
            r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],reads
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build()
    if not candidate['fits']:raise ValueError('Envelope')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10494','--stop-address=0x104dc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-mic-frame/index.disassembly.txt').read_text());cases=0
    def check(channel,frame,index,count,per_context,per_channel,length,rate,base):
        nonlocal cases
        words={0x20050000:0x20027b60,0x20050008:index,0x20027b9c:count,
               0x20027b84:per_context,0x20027b88:per_channel,0x20027b7c:length,
               0x20027b80:rate,0x20027bb0:base}
        memory={a+i:b for a,value in words.items() for i,b in enumerate(value.to_bytes(4,'little'))}
        samples=((length*rate)&MASK)//1000
        expected=(base+(frame+channel*per_channel+(index%count)*per_context)*samples*2)&MASK
        for code,entry in ((old,0x10494),(new,0x10206f08)):
            result,reads=execute(code,entry,memory,channel,frame,index^base)
            if result!=expected or sorted(reads)!=sorted(words):raise ValueError('Frame arithmetic/read set')
        cases+=1
    # All normal three-context microphone slots, including index wraparound.
    for channel,frame,index in product(range(2),range(4),range(256)):
        check(channel,frame,index,3,4,12,10,16000,0x20030410)
    values=(0,1,3,4,12,999,1000,16000,0x7fffffff,0x80000000,0xffffffff)
    baseline=[1,3,2,3,4,12,10,16000,0x20030410]
    # Each pair of inputs varies together to expose overflow and reassociation.
    for left in range(9):
        for right in range(left+1,9):
            for a,b in product(values,values):
                args=baseline.copy();args[left]=a;args[right]=b
                if args[3]:check(*args)
    import random
    rng=random.Random(0x10494)
    for _ in range(2000):
        args=[rng.getrandbits(32) for _ in range(9)];args[3]=args[3] or 1;check(*args)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-mic-frame/index.elf',output/'index.elf')
    symbol='open_cfw_gx8002_mic_frame'
    return {'functions':[{'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
      'stock_occurrences':[{'symbol':symbol,'package_offset':0x10494,'bytes':72,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'candidate':candidate,'decoded_cases':cases,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_mic_frame.py','build_gx8002_mic_frame.py','verify_gx8002_memcpy_source.py')},
      'limits':['Valid aligned context/header and nonzero context count required. Exact read set and arithmetic checked under stable ordinary RAM; read order differs. Boundary return addresses are arithmetic-only cases. No physical concurrency or timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-mic-frame-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
