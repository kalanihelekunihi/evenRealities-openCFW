# SPDX-License-Identifier: MIT
"""Compose DMA allocation/release with source CSI state and upstream clock gate."""
import json,struct
from itertools import product
from verify_gx8002_backup_dma_current_registration import authenticated_code,ROOT,Elf32
from verify_gx8002_backup_dma_select import execute as select
from verify_gx8002_backup_dma_deallocate import execute as release
from verify_gx8002_backup_irq_state import execute as irq
from compare_gx8002_backup_platform_gate import execute as gate,oracle
from compare_gx8002_backup_clock_lookup import execute as lookup


def verify():
    code={};hashes={}
    targets=[('select','backup-dma-select','select.elf'),('release','backup-dma-shared','pair.elf'),
             ('irq','backup-irq-state','state.elf'),('gate','backup-platform-gate','gate.elf'),
             ('lookup','backup-clock-lookup','tables.elf')]
    for key,kind,artifact in targets:
        code[key],hashes[key]=authenticated_code(kind,artifact,'gx8002-'+kind+'-source-verification.json')
    tables=Elf32((ROOT/'build/gx8002-source-candidate/backup-clock-lookup/tables.elf').read_bytes(),'clock')
    table=tables.contents(next(s for s in tables.sections if s['name']=='.data.gx_clock_param_table'))
    gates=Elf32((ROOT/'build/gx8002-source-candidate/backup-platform-gate/gate.elf').read_bytes(),'gate')
    jumps=gates.contents(next(s for s in gates.sections if s['name']=='.rodata'))
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    helpers={0x1000486c:0x10025560,0x10004878:0x1002556c,0x10003be8:0x10025080}
    cases=cycles=clock_calls=0;state=0x2002d3e8
    for flags,count,token,source in product(product((0,1,2,255),repeat=2),(0,1,2,3,0xffffffff),
                                          (0,0x40,0xffffffff,0x12345678),(0,0xffffffff,0x55555555,0xaaaaaaaa)):
        psr=token;events=[]
        def irq_hook(save,argument):
            nonlocal psr
            before=psr
            value,psr,trace=irq(code['irq'],0x1000486c if save else 0x10004878,psr,argument)
            events.append(('save' if save else 'restore',before,psr))
            return value
        def gate_hook(module,enabled):
            nonlocal clock_calls
            assert psr==token&~0x40
            def lookup_hook(mod):return lookup(code['lookup'],0x100034e0,mod,0x1000,ids)
            trace=gate(code['gate'],0x10003be8,jumps,table,module,enabled,source,0,lookup_hook=lookup_hook)
            assert trace==oracle(table,module,enabled,source)
            events.append(('gate',module,enabled,trace));clock_calls+=1
        channel,trace,memory=select(code['select'],0x10004b6c,flags,token,0,count=count,
                                   helper_addresses=helpers,irq_hook=irq_hook,gate_hook=gate_hook)
        expected=next((ch for ch in range(min(count,2)) if flags[ch]==0),0xffffffff)
        assert channel==expected and psr==token
        if channel!=0xffffffff:
            updated=tuple(memory[state+0x370+i] for i in range(2))
            release_trace,final=release(code['release'],0x10004bc0,updated,token,channel,count=count,
                                        helper_addresses=helpers,irq_hook=irq_hook,gate_hook=gate_hook)
            assert psr==token and final=={state+4:count,**{state+0x370+i:v for i,v in enumerate(flags)}}
            wanted=[(25,1)]
            if not any(v==1 for v in flags[:min(count,2)]):wanted.append((25,0))
            assert [(e[1],e[2]) for e in events if e[0]=='gate']==wanted
            cycles+=1
        else:assert not any(e[0]=='gate' for e in events)
        cases+=1
    report={'artifact_sha256':hashes,'cases':cases,'successful_cycles':cycles,'compiled_clock_calls':clock_calls,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled allocator/deallocator, CSI PSR operations, upstream clock gate and lookup compose through explicit call hooks.',
                      'Independent frames and modeled PSR/MMIO values; physical interrupts, clock hardware and concurrency remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dma-clock-cycle.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    r=verify();print(r['cases'],'cases;',r['successful_cycles'],'cycles;',r['compiled_clock_calls'],'clock calls')
