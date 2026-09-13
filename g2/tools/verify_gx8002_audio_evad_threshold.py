# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_audio_evad_threshold import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_audio_evad_threshold import execute,ADDRESSES
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Threshold stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xda6c','--stop-address=0xdab8',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-evad-threshold/gain.disassembly.txt').read_text());cases=0;repairs=0
    for source,config,seed in product((0,1,2,3,4,8,0xffffffff),product((0,1,0x80000000,0xffffffff),repeat=3),(0,0xa5a5a5a5,0xffffffff)):
        memory={a:seed^a for a in ADDRESSES};trace=[];result=0xffffffff
        if source in (1,2,4):
            result=0;base={1:0xa0a00010,2:0xa0a00030,4:0xa0a00050}[source]
            if source!=1:
                trace.append(('read',base,memory[base]));memory[base]&=~(1<<28);trace.append(('write',base,memory[base]))
            for off,value in zip((8,12,16),config):memory[base+off]=value;trace.append(('write',base+off,value))
            if execute(old,0xda6c,source,config,seed,0)!=(result,trace,memory):raise ValueError('Threshold stock oracle')
            cases+=1
        else:repairs+=1
        if execute(new,0x102044e0,source,config,seed,0)!=(result,trace,memory):raise ValueError('Threshold source oracle')
    return {'candidate':candidate,'decoded_cases':cases,'invalid_source_repair_cases':repairs,'source_admitted':False,'hardware_qualified':False,'limits':['Ordered word stores, independent channels and aggregate ABI checked. Invalid selectors intentionally return -1 without MMIO. Candidate fits the stock envelope; export admission pending. Physical thresholds unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-evad-threshold-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],r['invalid_source_repair_cases'])
