# SPDX-License-Identifier: MIT
"""Decoded volume effects, signed ABI, and getter output aliasing."""
import json,re,subprocess
from build_gx8002_audio_output_volume import build,ROOT,IMAGE_SHA,sha,Elf32,IMAGE
from verify_gx8002_memcpy_source import decode
HANDLE=0x20010000
TABLE=0x1020a910
REG=0xa0b00014

def signed(value,bits=32):
    value&=(1<<bits)-1
    return value-(1<<bits) if value>>(bits-1) else value

def execute(code,entry,argument,seed,cached,table,getter=False):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=HANDLE,r1=argument&0xffffffff);saved=r.copy();memory={a:0xa5 for a in range(HANDLE,HANDLE+64)};memory[HANDLE+18]=cached&255;memory[HANDLE+19]=(cached>>8)&255;word=seed;trace=[];pc=entry;condition=False
    for _ in range(400):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Volume ABI')
            return r['r0'],trace,word,memory
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('min.s32','max.s32'):r[p[0]]=(min if op=='min.s32' else max)(signed(r[p[1]]),signed(r[p[2]]))&0xffffffff
        elif op in ('addi','subi'):r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='addu':r[p[0]]=((r[p[1]]+r[p[2]]) if len(p)==3 else (r[p[0]]+r[p[1]]))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op=='andn':r[p[0]]=r[p[1]]&~r[p[2]]
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&0xffffffff
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:jump=int(p[1],0)
        elif op in ('ld.w','st.w','ld.h','ld.hs','st.h','ldr.h','ldr.hs'):
            if op.startswith('ldr'):
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args);reg,base,index=m.groups();address=(r[base]+4*r[index])&0xffffffff
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups();address=(r[base]+int(offset,0))&0xffffffff
            size=4 if op.endswith('w') else 2
            if address==REG:
                if size!=4:raise ValueError('Volume MMIO width')
                if op=='ld.w':r[reg]=word;trace.append(('read',REG,word))
                elif op=='st.w':word=r[reg];trace.append(('write',REG,word))
                else:raise ValueError('Volume MMIO opcode')
            elif TABLE<=address<TABLE+len(table)-1:
                if op.startswith('st') or size!=2:raise ValueError('Volume table access')
                value=int.from_bytes(table[address-TABLE:address-TABLE+2],'little');r[reg]=(signed(value,16)&0xffffffff) if op.endswith('hs') else value
            elif address in memory and address+1 in memory:
                if size!=2:raise ValueError('Volume RAM width')
                if op.startswith('st'):
                    value=r[reg]&65535;memory[address]=value&255;memory[address+1]=value>>8;trace.append(('write_half',address,value))
                else:
                    value=memory[address]|memory[address+1]<<8;r[reg]=(signed(value,16)&0xffffffff) if op.endswith('hs') else value;trace.append(('read_half',address,value))
            else:raise ValueError(('Volume address',hex(address),op))
        else:raise ValueError('Volume opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Volume execution bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper));stock=IMAGE.read_bytes()
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe51c','--stop-address=0xe5b8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-volume/bits.disassembly.txt').read_text());table=stock[0x13e9c:0x13f30];stock_table=stock[0x13e9c:0x13f34];gains=[int.from_bytes(table[i:i+2],'little') for i in range(0,148,4)];cases=0
    for value in range(-32768,32768):
        seed=0xa5a5a5a5;gain=gains[min(18,max(-18,value))+18];word=(seed&~0x3ff0000)|(gain<<16);trace=[('read',REG,seed),('write',REG,word),('write_half',HANDLE+18,value&65535)];memory={a:0xa5 for a in range(HANDLE,HANDLE+64)};memory[HANDLE+18]=value&255;memory[HANDLE+19]=(value>>8)&255;wanted=(0,trace,word,memory)
        for code,entry,data in ((old,0xe51c,stock_table),(new,0x10204f90,table)):
            if execute(code,entry,value,seed,0x1234,data)!=wanted:raise ValueError(('Setter effects',entry,value))
        cases+=1
    getter_cases=0
    for gain in range(1024):
        for pointer in (HANDLE+16,HANDLE+18,HANDLE+20):
            for cached in (0,0x7fff,0x8000,0xffff):
                seed=(0xa5a5a5a5&~0x3ff0000)|(gain<<16);mapped=gains.index(gain)-18 if gain in gains else 1;memory={a:0xa5 for a in range(HANDLE,HANDLE+64)};memory[HANDLE+18]=cached&255;memory[HANDLE+19]=cached>>8;memory[pointer]=mapped&255;memory[pointer+1]=(mapped>>8)&255;observed=memory[HANDLE+18]|memory[HANDLE+19]<<8;wanted=(signed(observed,16)&0xffffffff,[('read',REG,seed),('write_half',pointer,mapped&65535),('read_half',HANDLE+18,observed)],seed,memory)
                for code,entry,data in ((old,0xe57c,stock_table),(new,0x10204ff0,table)):
                    if execute(code,entry,pointer,seed,cached,data,True)!=wanted:raise ValueError(('Getter effects',entry,gain,pointer,cached))
                getter_cases+=1
    return {'candidate':candidate,'signed_setter_cases':cases,'getter_cases':getter_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Setter signed16 ABI inputs; getter all1024 codes with aligned adjacent/alias output and four cached signs. Source unknown-code fallback preserves stock adjacent-data result1 without overread. Physical gain accuracy and asynchronous register mutation unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-volume-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['signed_setter_cases'],r['getter_cases'])
