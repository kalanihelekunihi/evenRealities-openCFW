# SPDX-License-Identifier: MIT
"""Compose admitted allocator and deallocator through concrete flag writes."""
import json
from itertools import product
from verify_gx8002_backup_dma_current_registration import authenticated_code, ROOT
from verify_gx8002_backup_dma_select import execute as select
from verify_gx8002_backup_dma_deallocate import execute as release


def verify():
    allocator,allocator_sha=authenticated_code('backup-dma-select','select.elf','gx8002-backup-dma-select-source-verification.json')
    deallocator,deallocator_sha=authenticated_code('backup-dma-shared','pair.elf','gx8002-backup-dma-shared-source-verification.json')
    helpers={0x1000486c:0x10025560,0x10004878:0x1002556c,0x10003be8:0x10025080}
    state=0x2002d3e8;cases=cycles=0
    for flags,count,token in product(product((0,1,2,255),repeat=3),(0,1,2,3,0xffffffff),(0,0x98765432)):
        channel,events,memory=select(allocator,0x10004b6c,flags,token,0,count=count,helper_addresses=helpers)
        expected=next((ch for ch in range(min(count,2)) if flags[ch]==0),0xffffffff)
        assert channel==expected and events[-1]==('irq_restore',token)
        if channel!=0xffffffff:
            updated=tuple(memory[state+0x370+i] for i in range(3))
            assert updated[channel]==1
            final_events,final_memory=release(deallocator,0x10004bc0,updated,token,channel,count=count,helper_addresses=helpers)
            assert final_memory=={state+4:count,**{state+0x370+i:v for i,v in enumerate(flags)}}
            assert [e for e in events if e[0]=='resource']==[('resource',25,1)]
            expected_release=[] if any(v==1 for v in flags[:min(count,2)]) else [('resource',25,0)]
            assert [e for e in final_events if e[0]=='resource']==expected_release
            assert final_events[0]==('irq_save',) and final_events[-1]==('irq_restore',token)
            cycles+=1
        else:
            assert memory=={state+4:count,**{state+0x370+i:v for i,v in enumerate(flags)}}
            assert not any(e[0] in ('write','resource') for e in events)
        cases+=1
    report={'allocator_elf_sha256':allocator_sha,'deallocator_elf_sha256':deallocator_sha,
            'cases':cases,'successful_allocation_release_cycles':cycles,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled routines composed using actual allocation-table output as deallocator input.',
                      'Preserves stock asymmetry: allocation requires zero while release considers exactly one active.',
                      'IRQ and resource primitives modeled; no physical concurrency or clock timing qualification.']}
    (ROOT/'docs/research/gx8002-backup-dma-allocation-cycle.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(verify(),indent=2))
