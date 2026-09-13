# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_backup_dma_descriptors import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_backup_dma_descriptors import execute

def verify(bus_hook=None):
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d210','--stop-address=0x3d314',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-descriptors/descriptors.disassembly.txt').read_text());cases=0
    for count,length,src,dst,width in product((0,1,2,3,17),(0,1,4095,4096,8190,-1),(0,1,2,3),(0,1,2,3),(0,1,4,255)):
        control=0x18000000|(src<<9)|(dst<<7)
        a=execute(old,0x3d210,count,length,control,width,bus_address=0x3db04,bus_hook=bus_hook);b=execute(new,0x100048d0,count,length,control,width,bus_address=0x100051c4,bus_hook=bus_hook)
        if a!=b:raise ValueError(('Descriptor mismatch',count,length,src,dst,width,a,b))
        if bus_hook is None:
            expected=bytearray([0xa5]*432)
            increments=(4095,0xf001,0,0)
            descriptors=max(count,1)
            remainder=length-(abs(length)//4095)*(-4095 if length<0 else 4095)
            for index in range(descriptors):
                last=index==descriptors-1
                source_value=(0xfffffff0+increments[src]*width*index)&0xffffffff
                destination_value=(0x20000000+increments[dst]*width*index)&0xffffffff
                next_address=0 if last else (0x20050000+(index+1)*24)&0x0fffffff
                words=(source_value,destination_value,next_address,
                       control&~0x18000000 if last else control,
                       (remainder if remainder else 4095)&0xffffffff if last else 4095)
                for word,value in enumerate(words):
                    start=index*24+word*4
                    expected[start:start+4]=value.to_bytes(4,'little')
            assert a[0]==bytes(expected), 'independent descriptor contents/untouched words'
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite separate pattern/output states with ordered pattern reads, descriptor writes and translation calls; saved frame abstracted and translation modeled. Candidate fits stock envelope; source admission remains pending.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-dma-descriptors-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Descriptor decoded cases:',result['decoded_cases'])
