# SPDX-License-Identifier: MIT
"""Qualify decoded buffer-index arithmetic and mapped memory accesses."""
import json,re,subprocess,shutil
from itertools import product
from build_gx8002_logfbank_index import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff


def execute(code,entry,memory,index,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=0x20050000,r1=index);initial=r.copy();pc=entry;reads=[]
    for _ in range(24):
        op,args,w=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='ld.w':
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(offset,0))&MASK
            if address%4 or any(address+i not in memory for i in range(4)):raise ValueError('Unmapped read')
            r[reg]=int.from_bytes(bytes(memory[address+i] for i in range(4)),'little');reads.append(address)
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
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10438','--stop-address=0x10454',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-logfbank-index/index.disassembly.txt').read_text());cases=0
    values=(0,1,4,40,48,0x7fffffff,0x80000000,0xffffffff)
    for index,frames,count,dimension,base in product(values,values,(1,3,48,0x7fffffff,0x80000000,0xffffffff),values,(0,0x20032210,0xfffffff0)):
        words={0x20050000:0x20027b60,0x20027b84:frames,0x20027b90:count,0x20027bcc:dimension,0x20027bd0:base}
        memory={address+i:b for address,value in words.items() for i,b in enumerate(value.to_bytes(4,'little'))}
        expected=(base+(((index*frames)&MASK)%count)*dimension*2)&MASK
        reads=[0x20050000,0x20027b84,0x20027b90,0x20027bcc,0x20027bd0]
        for code,entry in ((old,0x10438),(new,0x10206eac)):
            if execute(code,entry,memory,index,(index^frames^base))!=(expected,reads):raise ValueError('Index/read effects')
        cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-logfbank-index/index.elf',output/'index.elf')
    symbol='open_cfw_gx8002_logfbank_index'
    return {'functions':[{'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
      'stock_occurrences':[{'symbol':symbol,'package_offset':0x10438,'bytes':28,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'candidate':candidate,'decoded_cases':cases,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_logfbank_index.py','build_gx8002_logfbank_index.py','verify_gx8002_memcpy_source.py')},
      'limits':['Requires valid aligned context/header and nonzero frame count. Unsigned wraparound and exact read order checked; returned arithmetic addresses need not refer to allocated storage in boundary cases. No dereference of computed pointer, concurrent mutation or physical timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-logfbank-index-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
