# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_backup_dma_transfer import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


from verify_gx8002_dma_transfer import execute

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d60c','--stop-address=0x3d654',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-transfer/transfer.disassembly.txt').read_text());cases=0
    for args in product((0,0x20060000),(0,0xa0000000),(0,416,0xffffffff),(0,1),(0,0x20040000),(0,1,0x80000000,0xffffffff),(0xa1000000,0xa1001000)):
        a=execute(old,0x3d60c,*args,state_address=0x2002d3e8,helper_addresses={0x3d314:0x102038f4,0x3d7b4:0x10025664});b=execute(new,0x10004ccc,*args,state_address=0x2002d3e8,helper_addresses={0x100049d4:0x102038f4,0x10004e74:0x10025664})
        if a!=b:raise ValueError(('Transfer comparison',args,a,b))
        destination,source,length,channel,config,status,base=args
        if a[0]!=(0xffffffff if status==0xffffffff else 0):raise ValueError('Transfer return')
        calls=[x for x in a[1] if x[0] in ('configure','cache')]
        wanted=[('configure',destination,source,length,channel,config)]
        if status!=0xffffffff:wanted.append(('cache',0x20050000,416))
        if calls!=wanted:raise ValueError('Transfer forwarding')
        writes=[x for x in a[1] if x[0]=='write' and x[1]>=0xa0000000]
        wanted=[] if status==0xffffffff else [('write',0xa1000310,257<<channel),('write',base+0x3a0,257<<channel)]
        if writes!=wanted:raise ValueError('Transfer MMIO oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Initialized channel domain 0/1; configuration and cache modeled. Tests include device-base change across cache boundary. Candidate size is checked by the admission wrapper.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-dma-transfer-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Transfer cases:',result['decoded_cases'])
