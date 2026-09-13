# SPDX-License-Identifier: MIT
"""Qualify exact KWS-init wrapper with modeled returning helpers."""
import json,subprocess,shutil,re
from itertools import product
from build_gx8002_kws_initialize import build,ROOT,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

def execute(code,callback,mode,helper_return):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=callback,r1=mode,r14=0x20070000);initial=r.copy();pc=0x10206d90;saved=None;condition=False;events=[]
    for _ in range(30):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+w
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],events
        elif op in ('movi','mov','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)
            if target not in (0x10206cb0,0x10205cf4):raise ValueError('Call target')
            events.append(('call',target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xab000000+i
            r['r0']=helper_return
        elif op=='st.w':
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
            if address!=0x20027b50:raise ValueError('Publication address')
            events.append(('publish',address,r[reg]))
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build();code=decode((ROOT/'build/gx8002-kws-initialize/init.disassembly.txt').read_text());cases=0
    # The builder requires exact equality of every linked instruction/literal
    # to authenticated stock, so this decoder executes both implementations.
    for callback,mode,result in product((0,1,0x10026340,0x7fffffff,0x80000000,0xffffffff),(*range(256),0x7fffffff,0x80000000,0xffffffff),(0,1,0xffffffff,0x80000000)):
        wanted=[]
        if mode<2:wanted.append(('call',0x10206cb0))
        wanted += [('call',0x10205cf4),('publish',0x20027b50,callback)]
        if execute(code,callback,mode,result)!=(0,wanted):raise ValueError('Initialization effects')
        cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-kws-initialize/init.elf',output/'init.elf')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0x1031c,'bytes':28,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    return {'functions':[row],'candidate':candidate,'decoded_cases':cases,'source_admitted':True,'hardware_qualified':False,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_kws_initialize.py','build_gx8002_kws_initialize.py','verify_gx8002_memcpy_source.py')},'limits':['Helper bodies modeled with caller clobbers; no physical startup/timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
