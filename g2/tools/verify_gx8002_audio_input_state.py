# SPDX-License-Identifier: MIT
"""Qualify state getter and unsigned wrapping read-index update."""
import json,re,subprocess,shutil
from itertools import product
from build_gx8002_audio_input_state import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
STATE=0x2002ecb0;MASK=0xffffffff


def execute(code,entry,memory,offset):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r0']=offset;initial=r.copy();pc=entry;events=[];condition=False
    for _ in range(20):
        op,args,w=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+w
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bf'):
            if op=='br' or not condition:nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            reg,base,disp=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(disp,0)
            if address not in memory:raise ValueError('State bounds')
            if op=='ld.w':r[reg]=memory[address];events.append(('read',address,r[reg]))
            else:memory[address]=r[reg];events.append(('write',address,r[reg]))
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('Leaf ABI')
            return r['r0'],events
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10920','--stop-address=0x10948',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-state/buffers.disassembly.txt').read_text())
    values=(0,1,2,3,255,256,0x7fffffff,0x80000000,0xfffffffe,0xffffffff);cases=0
    for read,write,offset in product(values,values,values):
        memory={STATE-4:0xdeadbeef,STATE:read,STATE+4:write,STATE+8:0xa5a5a5a5,STATE+12:offset,STATE+16:0x12345678}
        next_index=(read+offset)&MASK;accepted=next_index<=write
        events=[('read',STATE,read),('read',STATE+4,write)]
        if accepted:events.append(('write',STATE,next_index))
        expected=memory.copy()
        if accepted:expected[STATE]=next_index
        for code,base in ((old,0),(new,0x101f6a74)):
            actual=memory.copy()
            if execute(code,0x1092c+base,actual,offset)!=(0 if accepted else MASK,events) or actual!=expected:raise ValueError('Read-index effects')
            actual=memory.copy()
            if execute(code,0x10920+base,actual,offset)!=(offset,[('read',STATE+12,offset)]) or actual!=memory:raise ValueError('Delayed VAD')
        cases+=1
    functions=[]
    for c in candidate['functions']:
        if not c['fits']:raise ValueError('State envelope')
        row={k:c[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['stock_occurrences']=[{'symbol':c['symbol'],'package_offset':c['package_offset'],'bytes':c['stock_envelope_bytes'],'sha256':c['stock_sha256'],'region':'image_a_xip_text'}];functions.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-input-state/buffers.elf',output/'state.elf')
    return {'functions':functions,'candidate':candidate,'decoded_cases':cases,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_audio_input_state.py','build_gx8002_audio_input_state.py','verify_gx8002_memcpy_source.py')},
      'limits':['Recovered unsigned wraparound preserved, including negative signed offsets. Fixed mapped RAM; exact ordered reads/write and neighboring state checked. No asynchronous producer/consumer or physical timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-state-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
