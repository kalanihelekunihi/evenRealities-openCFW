# SPDX-License-Identifier: MIT
"""Compose decoded callback registration with original-entry DMA IRQ source."""
import json
from itertools import product
from build_gx8002_backup_dma_callback import build as callback_build,ROOT
from build_gx8002_backup_dma_shared import build as shared_build
from verify_gx8002_backup_dma_callback import execute as register
from verify_gx8002_backup_dma_irq import execute as dispatch
from verify_gx8002_memcpy_source import decode

def verify():
    builds={'callback':callback_build(),'shared':shared_build()}
    setter=decode((ROOT/'build/gx8002-backup-dma-callback/callback.disassembly.txt').read_text())
    handler=decode((ROOT/'build/gx8002-backup-dma-shared-pool/pair.disassembly.txt').read_text())
    cases=0
    for c0,c1,p0,p1,pending in product((0,0x10004034),(0,0x10004054),(0,0x12345678),(0,0xffffffff),(0,1,2,3,0x80000003)):
        memory={};writes=[]
        for channel,callback,private in ((0,c0,p0),(1,c1,p1)):
            stores=register(setter,0x10004cb8,channel,callback,private)
            writes.extend(stores);memory.update(stores)
        assert set(memory)=={0x200174a8,0x200174ac,0x200174b0,0x200174b4}
        callbacks=tuple(memory[0x200174a8+4*i] for i in range(2))
        private=tuple(memory[0x200174b0+4*i] for i in range(2))
        result,trace,final=dispatch(handler,0x10004c04,pending,callbacks,False,0,private_data=private,helper_addresses={0x10004bc0:0x10203a98})
        wanted=[('callback',cb,pr) for i,(cb,pr) in enumerate(((c0,p0),(c1,p1))) if pending&(1<<i) and cb]
        assert result==0 and [item for item in trace if item[0]=='callback']==wanted
        assert all(final[address]==value for address,value in memory.items())
        assert [item for item in trace if item[0]=='deallocate']==[('deallocate',i) for i in range(2) if pending&(1<<i)]
        cases+=1
    return {'builds':builds,'cases':cases,'source_admitted':False,'limits':['Valid two-channel registrations handed off through concrete stored table words.','Callback bodies and deallocation remain modeled; initialization and physical interrupts are separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-callback-dispatch.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'composition cases passed')
