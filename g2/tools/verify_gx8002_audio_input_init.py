# SPDX-License-Identifier: MIT
"""Decode initialization callback ABI, nested clearing and publication order."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_init import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x101f6a74;STATE=0x2002ecb0;CALLBACK=0x2002dfa0


def execute(code,entry,callback,result,seed,clear_code,clear_entry):
    from compare_gx8002_memset import execute as clear
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r.update(r0=callback,r14=0x20070000);initial=r.copy();saved=None;pc=entry;events=[]
    memory={a:(a*37+seed)&255 for a in range(STATE-4,STATE+24)};memory.update({a:0xa5 for a in range(CALLBACK-4,CALLBACK+8)});before=memory.copy()
    def write(address,value):
        if address%4 or address not in (r['r14'],CALLBACK):raise ValueError('Store bounds')
        for i,b in enumerate(value.to_bytes(4,'little')):memory[address+i]=b
    for _ in range(40):
        op,args,w=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            wanted=before.copy()
            for a in range(STATE,STATE+20):wanted[a]=0
            for i,b in enumerate(callback.to_bytes(4,'little')):wanted[CALLBACK+i]=b
            if any(memory[a]!=b for a,b in wanted.items()):raise ValueError('Final memory')
            return r['r0'],events
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addi','subi'):
            if p[0]!='r14' or p[1]!='r14' or p[2]!='24':raise ValueError('Locals')
            r['r14']+=24 if op=='addi' else -24
        elif op=='st.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);write(address,r[reg])
            if address==CALLBACK:events.append(('publish',r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(BASE if entry==0x10948 else 0))&0xffffffff
            if target==0x102099cc:
                if tuple(r[f'r{i}'] for i in range(3))!=(STATE,0,20):raise ValueError('Clear arguments')
                trace=clear(clear_code,clear_entry,STATE,0,20,seed)
                if trace['result']!=STATE:raise ValueError('Clear return')
                for address,size,value in trace['trace']:
                    if not STATE<=address or address+size>STATE+20:raise ValueError('Clear bounds')
                    for i,b in enumerate(value.to_bytes(size,'little')):memory[address+i]=b
                events.append(('clear',));returned=STATE
            elif target==0x102047e4:
                args=tuple(r[f'r{i}'] for i in range(4))+(int.from_bytes(bytes(memory[r['r14']+i] for i in range(4)),'little'),)
                if args!=(0x10026214,0x10207234,0x10207020,0,0):raise ValueError('Callback struct')
                if any(memory[a] for a in range(STATE,STATE+20)) or any(memory[a]!=before[a] for a in range(CALLBACK,CALLBACK+4)):raise ValueError('Driver entry state')
                events.append(('init',args));returned=result
            else:raise ValueError('Target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xab000000+i)&0xffffffff
            r['r0']=returned
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Bound')


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    from build_gx8002_memset_candidate import build as clear_build
    clear_evidence=clear_build()
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10948','--stop-address=0x10984',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-init/index.disassembly.txt').read_text())
    clear_old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x12f58','--stop-address=0x12ff8',str(wrapper)],text=True));clear_new=decode((ROOT/'build/gx8002-board/memset-candidate.disassembly.txt').read_text());cases=0
    for callback,result,seed in product((0,1,0x10026214,0x80000000,0xffffffff),(0,1,0x80000000,0xffffffff),(0,1,0xa5a5a5a5,0xffffffff)):
        wanted=(result,[('clear',),('init',(0x10026214,0x10207234,0x10207020,0,0)),('publish',callback)])
        for code,entry in ((old,0x10948),(new,0x102073bc)):
            for helper,helper_entry in ((clear_old,0x12f58),(clear_new,0x102099cc)):
                if execute(code,entry,callback,result,seed,helper,helper_entry)!=wanted:raise ValueError('Initialization')
                cases+=1
    return {'candidate':candidate,'nested_decoded_cases':cases,'clear_evidence':clear_evidence,'source_admitted':False,'limits':['Nested stock/source clears, callback ABI, driver-entry state, delayed publication and return propagation checked. Driver body modeled; admission pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-init-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['nested_decoded_cases'])
