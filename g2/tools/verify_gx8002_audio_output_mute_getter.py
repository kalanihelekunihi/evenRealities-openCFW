# SPDX-License-Identifier: MIT
"""Signed cached mute getter and setter/getter composition."""
import json,subprocess
from build_gx8002_audio_output_mute import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_audio_output_mute import execute as setter
from verify_gx8002_memcpy_source import decode

def execute(code,entry,handle,status):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=handle;saved=r.copy();trace=[];pc=entry
    for _ in range(4):
        op,args,width=code[pc]
        if op in ('ld.hs','ld.h'):
            if args!='r0, (r0, 0x10)' or r['r0']!=handle:raise ValueError('Mute getter operand')
            raw=int.from_bytes(status[:2],'little');value=int.from_bytes(status[:2],'little',signed=op=='ld.hs')&0xffffffff
            trace.append(('read_halfword',handle+16,raw));r['r0']=value
        elif op=='sexth':
            if args!='r0, r0':raise ValueError('Getter sign extension operand')
            r['r0']=(r['r0']&65535)+(0xffff0000 if r['r0']&32768 else 0)
        elif op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Mute getter ABI')
            return r['r0'],trace,status
        else:raise ValueError('Mute getter instruction '+op)
        pc+=width
    raise ValueError('Mute getter bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Getter stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe260','--stop-address=0xe658',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-mute/bits.disassembly.txt').read_text());cases=0
    for value in range(65536):
        status=value.to_bytes(2,'little')+bytes((0xa5,0x5a));expected=value if value<32768 else value+0xffff0000
        wanted=(expected,[('read_halfword',0x20010010,value)],status)
        if execute(old,0xe260,0x20010000,status)!=wanted or execute(new,0x10204cd4,0x20010000,status)!=wanted:raise ValueError('Signed getter mismatch')
        cases+=1
    nested=0
    for code,set_entry,get_entry in ((old,0xe618,0xe260),(new,0x1020508c,0x10204cd4)):
        for value in (0,1,2,0x80000000,0xffffffff):
            result,trace,memory,status=setter(code,set_entry,0x20010000,value,0xa5a5a5a5)
            returned,reads,after=execute(code,get_entry,0x20010000,status)
            if result!=0 or returned!=1 or after!=status:raise ValueError('Mute cached status composition')
            enabled=int(value!=0)
            if ((memory[0xa0b00004]>>9)&1)!=enabled or any(((memory[0xa0b00014]>>bit)&1)!=enabled for bit in (11,15)):raise ValueError('Mute hardware bits composition')
            nested+=1
    return {'candidate':candidate,'signed_getter_cases':cases,'setter_getter_cases':nested,'source_admitted':False,'hardware_qualified':False,'limits':['All16-bit cached values sign-extended as stock. Setter/getter composition preserves stock unmute/status discrepancy. Physical execution and broader driver state remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-mute-getter-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['signed_getter_cases'],r['setter_getter_cases'])
