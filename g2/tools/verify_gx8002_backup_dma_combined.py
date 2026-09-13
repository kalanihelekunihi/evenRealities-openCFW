# SPDX-License-Identifier: MIT
"""Compare combined source layout to separately qualified backup routines."""
import json
from itertools import product
from build_gx8002_backup_dma_combined import build,ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_dma_irq import execute as irq,expected
from verify_gx8002_backup_dma_initialize import execute as initialize
from verify_gx8002_backup_dma_deallocate import execute as deallocate

def verify():
    candidate=build()
    combined=decode((ROOT/'build/gx8002-backup-dma-combined/combined.disassembly.txt').read_text())
    standalone=decode((ROOT/'build/gx8002-backup-dma-irq/irq.disassembly.txt').read_text())
    counts={'irq':0,'initialize':0,'deallocate':0}
    for pending,c0,c1,mutation,status in product((0,1,2,3,4,0x80000000,0xffffffff),(0,0x10004054),(0,0x10004034),(False,True),(0,1,0xffffffff)):
        args=(pending,(c0,c1),mutation,status)
        a=irq(standalone,0x10004c04,*args,helper_addresses={0x10004bc0:0x10203a98})
        b=irq(combined,0x10004c08,*args,helper_addresses={0x10004bc0:0x10203a98})
        assert a==b and b[0]==0 and b[1]==expected(pending,(c0,c1),mutation)
        counts['irq']+=1
    standalone=decode((ROOT/'build/gx8002-backup-dma-initialize/initialize.disassembly.txt').read_text())
    for args in product((0,0xffffffff,0x12345678),(0xa1000000,0xa1001000),(0,1,0xffffffff)):
        kw={'state':0x2002d3e8,'gate':0x10003be8,'request_irq':0x10004844}
        old,m0=initialize(standalone,0x10004d14,*args,**kw)
        new,m1=initialize(combined,0x10004d14,*args,**kw)
        assert old[-1]==('irq',10,0x10004c04,0)
        assert new[-1]==('irq',10,0x10004c08,0)
        assert old[:-1]==new[:-1] and m0==m1
        counts['initialize']+=1
    standalone=decode((ROOT/'build/gx8002-backup-dma-deallocate/deallocate.disassembly.txt').read_text())
    helpers={0x1000486c:0x10025560,0x10004878:0x1002556c,0x10003be8:0x10025080}
    for flags,count,channel,token in product(product((0,1,2,255),repeat=3),(0,1,2,3,0xffffffff),range(3),(0,0x98765432)):
        args=(flags,token,channel)
        assert deallocate(standalone,0x10004bc0,*args,helper_addresses=helpers,count=count)==deallocate(combined,0x10004bc0,*args,helper_addresses=helpers,count=count)
        counts['deallocate']+=1
    return {'candidate':candidate,'decoded_cases':counts,'source_admitted':False,'limits':['Compared combined code to separately stock-qualified source routines with modeled helpers.','Relocated IRQ registration checked; external references, loader placement and hardware execution remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-combined-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
