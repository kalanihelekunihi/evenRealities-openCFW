# SPDX-License-Identifier: MIT
"""Check context selection and alias-sensitive publication ordering."""
import json,re,subprocess,shutil
from itertools import product
from build_gx8002_context_acquire import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff


def execute(code,entry,index,context_out,size_out,memory,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=index,r1=context_out,r2=size_out);initial=r.copy();pc=entry;writes=[]
    for _ in range(36):
        op,args,w=code[pc];p=[s.strip() for s in args.split(',')]
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('mult','addu','subu','addi','lsli'):
            if op in ('addi','lsli'):
                a,b=(r[p[0]],int(p[1],0)) if len(p)==2 else (r[p[1]],int(p[2],0))
            else:a,b=(r[p[0]],r[p[1]]) if len(p)==2 else (r[p[1]],r[p[2]])
            r[p[0]]=(a*b if op=='mult' else a-b if op=='subu' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='divu':r[p[0]]=r[p[1]]//r[p[2]]
        elif op in ('st.w','str.w'):
            if op=='st.w':
                reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(offset,0))&MASK
            else:
                reg,base,offset,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();address=(r[base]+(r[offset]<<int(shift)))&MASK
            if address%4 or any(address+i not in memory for i in range(4)):raise ValueError('Store bounds')
            writes.append((address,r[reg]))
            for i,b in enumerate(r[reg].to_bytes(4,'little')):memory[address+i]=b
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],writes
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build()
    if not candidate['fits']:raise ValueError('Envelope')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10454','--stop-address=0x10494',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-context-acquire/context.disassembly.txt').read_text());cases=0
    for index in (*range(256),0x7fffffff,0x80000000,0xfffffffd,0xfffffffe,0xffffffff):
        record=0x20027be0+(index%3)*8512
        positions=(0x20050000,0x20050004,record-4,record,record+4,record+16,record+20,record+32)
        for context_out,size_out in product(positions,positions):
            memory={a:((a+index)%255)+1 for a in range(record-8,record+40)}
            memory.update({a:0xa5 for a in range(0x2004fff8,0x20050010)})
            wanted=[(record,0x20027b60),(record+16,record+32),(context_out,record),(size_out,8512)]
            expected=memory.copy()
            for address,value in wanted:
                for i,b in enumerate(value.to_bytes(4,'little')):expected[address+i]=b
            for code,entry in ((old,0x10454),(new,0x10206ec8)):
                actual=memory.copy()
                if execute(code,entry,index,context_out,size_out,actual,index)!=(0,wanted) or actual!=expected:raise ValueError('Publication effects')
            cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-context-acquire/context.elf',output/'context.elf')
    symbol='open_cfw_gx8002_context_acquire'
    return {'functions':[{'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
      'stock_occurrences':[{'symbol':symbol,'package_offset':0x10454,'bytes':64,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'candidate':candidate,'decoded_cases':cases,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_context_acquire.py','build_gx8002_context_acquire.py','verify_gx8002_memcpy_source.py')},
      'limits':['Fixed three-record firmware layout; valid aligned writable output pointers required. Decoded output aliases checked, including same output word and record fields; no physical concurrency or timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-context-acquire-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
