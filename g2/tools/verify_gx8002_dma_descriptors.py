# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_dma_descriptors import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_dma_descriptors import execute

def verify(bus_hook=None):
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcdb4','--stop-address=0xce80',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-descriptors/descriptors.disassembly.txt').read_text());cases=0
    for count,length,src,dst,width in product((0,1,2,3,17),(0,1,4095,4096,8190,-1),(0,1,2,3),(0,1,2,3),(0,1,4,255)):
        control=0x18000000|(src<<9)|(dst<<7)
        a=execute(old,0xcdb4,count,length,control,width,bus_hook=bus_hook);b=execute(new,0x10203828,count,length,control,width,bus_hook=bus_hook)
        if a!=b:raise ValueError(('Descriptor mismatch',count,length,src,dst,width,a,b))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite separate pattern/output states with ordered pattern reads, descriptor writes and translation calls; saved frame abstracted and translation modeled. Candidate fits stock envelope; source admission remains pending.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-descriptors-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Descriptor decoded cases:',result['decoded_cases'])
