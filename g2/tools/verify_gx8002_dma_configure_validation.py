# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_dma_configure import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_dma_configure_validation import execute

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xce80','--stop-address=0xcfd8',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-configure/configure.disassembly.txt').read_text());cases=accepted=0
    for values in product((0,1,2,3,4,0xffffffff),repeat=6):
        fields=[0,3,0,6,1,0,4,0,0,0,0,2]
        for index,value in zip((7,2,9,4,10,5),values):fields[index]=value
        reads=[6,1,0];valid=True
        for index,limit in ((7,1),(2,1),(9,3),(4,3),(10,1),(5,1)):
            if index==10:reads.append(11)
            reads.append(index)
            if fields[index]>limit:valid=False;break
        if valid:reads.extend((8,3))
        wanted=('accepted' if valid else 'rejected',0 if valid else 0xffffffff,[('read',0x20040000+i*4,fields[i]) for i in reads])
        if execute(old,0xce80,fields)!=wanted or execute(new,0x102038f4,fields)!=wanted:raise ValueError(('Configuration validation',values))
        accepted+=int(valid);cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'accepted_cases':accepted,'source_admitted':False,'hardware_qualified':False,'limits':['Entry through first clear call or validation return only. Remaining configuration path not covered. Abstract saved frame; exact ordered config reads and no external writes on rejection.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-configure-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('Configuration validation cases:',result['decoded_cases'])
