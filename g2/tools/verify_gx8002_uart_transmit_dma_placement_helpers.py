# SPDX-License-Identifier: MIT
"""Execute relocated setup with authenticated decoded burst/callback helpers."""
import json,subprocess
from itertools import product
from build_gx8002_uart_transmit_dma_placement import build,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_transmit_dma import execute as setup
from verify_gx8002_uart_dma_burst import execute as burst
from verify_gx8002_dma_callback import execute as callback

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={};hashes={}
    for name,filename in [('uart-dma-burst','burst'),('dma-callback','callback')]:
        path=ROOT/f'build/gx8002-{name}/{filename}.elf';elf=Elf32(path.read_bytes(),name)
        report=json.loads((ROOT/f'docs/research/gx8002-{name}-verification.json').read_text())
        row=report['candidate']['functions'][0];section=next(s for s in elf.sections if s['name']=='.text')
        assert sha(elf.contents(section))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));hashes[name]=sha(path.read_bytes())
    code=decode((ROOT/'build/gx8002-uart-transmit-dma-placement/dma.disassembly.txt').read_text());cases=0
    mapping={1<<i:i-1 for i in range(2,11)}
    for port,channel,first,second in product((0,1,2,0xffffffff),(0,1,0xffffffff),(0,4,64,1024,0xffffffff),(8,128,512)):
        calls=[];writes=[]
        def burst_hook(descriptor,direction,index):
            assert descriptor==0x20026a94 and direction==1
            tx=first if index==0 else second
            value,reads=burst(codes['uart-dma-burst'],0x10203050,tx,32,direction)
            assert reads==[(0x20026ac8,tx),(0x20026acc,32)]
            calls.append(('burst',index));return value
        def callback_hook(number,handler,private):
            assert (number,handler,private)==(channel,0x102030c4,0x20026a94)
            actual=callback(codes['dma-callback'],0x10203b64,number,handler,private)
            assert actual==[(0x20027320+4*channel,handler),(0x20027328+4*channel,private)]
            writes.extend(actual);calls.append(('callback',))
        result,trace,memory=setup(code,0x10203108,port,0x20050000,80,channel,0,0,0xffffffff,burst_hook=burst_hook,callback_hook=callback_hook)
        success=channel!=0xffffffff and port<2
        assert result==(0 if success else 0xffffffff)
        assert calls==([] if channel==0xffffffff else [('burst',0),('burst',1)]+([('callback',)] if success else []))
        assert len(writes)==(2 if success else 0)
        transfers=[x for x in trace if x[0]=='transfer']
        assert transfers==([('transfer',0xa0000000,0x20050000,80,channel,(0,mapping.get(first,0),0,0,0,0,mapping.get(second,0),1,7 if port==0 else 5,1,0,1))] if success else [])
        assert [x for x in trace if x[0]=='release']==([('release',channel)] if channel!=0xffffffff and port>=2 else [])
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'helper_elf_sha256':hashes,'limits':['Original-entry redirect, burst helpers and callback writes execute decoded source; allocation/release and transfer internals remain separate qualifications. No physical DMA/timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-placement-helpers.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
