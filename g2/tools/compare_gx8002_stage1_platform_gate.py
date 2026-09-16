# SPDX-License-Identifier: MIT
"""Compare stage-one module-gate instructions and ordered register effects."""
import json,subprocess
from build_gx8002_stage1_platform_gate import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from compare_gx8002_backup_platform_gate import execute as run,oracle
from verify_gx8002_memcpy_source import decode


def execute(*args,**kwargs):
    return run(*args,**kwargs,record_base=0x200014c8,jump_base=0x10001324,lookup_entry=0x10000138)


def verify(lookup_hook=None):
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-stage1-platform-gate';p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x38b4c','--stop-address=0x38c54',str(p)],text=True))
    new=decode((out/'gate.disassembly.txt').read_text())
    e=Elf32((out/'gate.elf').read_bytes(),'gate');jumps=e.contents(next(s for s in e.sections if s['name']=='.rodata'))
    table_offset=0x200014c8-0x20000000+0x38954
    table=stock[table_offset:table_offset+416]
    jump_offset=0x10001324-0x10000000+0x38954
    cases=0
    for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
      for enable in (0,1,2,0xffffffff):
       for source in [0,0xffffffff,0x55555555,0xaaaaaaaa,*[1<<i for i in range(32)],*[(~(1<<i))&0xffffffff for i in range(32)]]:
        expected=oracle(table,module,enable,source)
        a=execute(old,0x38b4c,stock[jump_offset:jump_offset+148],table,module,enable,source,0x10000000-0x38954,lookup_hook=lookup_hook)
        b=execute(new,0x100001f8,jumps,table,module,enable,source,0,lookup_hook=lookup_hook)
        assert a==b==expected,(module,enable,source,a,b,expected)
        cases+=1
    report={'candidate':candidate,'cases':cases,'stock_table_offset':table_offset,'stock_table_sha256':sha(table),
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Backup module lookup modeled using authenticated stock table, not yet qualified source.',
                      'Ordered MMIO and lookup traces with source-generated branch tables; physical clocks, table mutations and placement remain unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-platform-gate-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(verify()['cases'],'stage1 gate cases passed')
