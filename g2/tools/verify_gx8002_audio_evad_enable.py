# SPDX-License-Identifier: MIT
"""Authenticated EVAD source qualification with independent ordered effects."""
import json,subprocess
from itertools import product
from build_gx8002_audio_evad_enable import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_audio_evad_enable import execute,ADDRESSES
from verify_gx8002_memcpy_source import decode

def oracle(source,config,seed,busy):
    memory={a:seed^a for a in ADDRESSES};trace=[]
    if source not in (1,2,4):return 0xffffffff,trace,memory
    base={1:0xa0a00010,2:0xa0a00030,4:0xa0a00050}[source]
    def field(address,low,bits,value):
        trace.append(('read',address,memory[address]));mask=((1<<bits)-1)<<low
        memory[address]=(memory[address]&~mask)|((value<<low)&mask)
        trace.append(('write',address,memory[address]))
    if source!=1:field(base,28,1,0)
    field(0xa0a00100,{1:18,2:19,4:20}[source],1,config[0])
    field(base,26,1,1)
    for _ in range(16 if busy is None else busy):trace.append(('read',base+20,0x80000001))
    if busy is None:return 'busy',trace,memory
    trace.append(('read',base+20,0))
    for low,bits,value in ((26,1,0),(27,1,int(config[0]==0)),(25,1,int(config[1]==0)),(24,1,1),(0,16,24576),(31,1,config[2])):field(base,low,bits,value)
    field(base+4,16,8,0);field(base+4,0,16,16)
    return 0,trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('EVAD stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd988','--stop-address=0xda6c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-evad-enable/gain.disassembly.txt').read_text());cases=0;repairs=0;stalls=0
    for source,config,seed,busy in product((1,2,4),product((0,1,2,0x80000000,0xffffffff),repeat=3),(0,0xa5a5a5a5,0xffffffff),(0,1,7,None)):
        wanted=oracle(source,config,seed,busy)
        if execute(old,0xd988,source,config,seed,busy)!=wanted or execute(new,0x102043fc,source,config,seed,busy)!=wanted:raise ValueError('EVAD effect oracle')
        cases+=1;stalls+=busy is None
    for source,seed in product((0,3,5,6,7,8,0x80000000,0xffffffff),(0,0xffffffff)):
        if execute(new,0x102043fc,source,(0xffffffff,2,1),seed,None)!=oracle(source,(0xffffffff,2,1),seed,None):raise ValueError('EVAD invalid-source repair')
        repairs+=1
    return {'candidate':candidate,'decoded_cases':cases,'persistent_busy_cases':stalls,'invalid_source_repair_cases':repairs,'source_admitted':False,'hardware_qualified':False,'limits':['Valid selectors compared against decoded stock and independent ordered word-MMIO oracle. Persistent busy checked as bounded polling prefix, not physical timing proof. Invalid selectors intentionally return -1 without MMIO instead of stock null access. Hardware energy detection unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-evad-enable-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],r['persistent_busy_cases'],r['invalid_source_repair_cases'])
