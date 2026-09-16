# SPDX-License-Identifier: MIT
"""Compare board hook branching and arguments at actual linked entries."""
import json,subprocess
from build_gx8002_stage1_clock_initialize import build,ROOT
from verify_gx8002_memcpy_source import decode


def execute(code,entry,helpers,result):
    pc=entry;value=None;trace=[];saved=False
    for _ in range(20):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r15' and not saved;saved=True
        elif op=='pop':assert args=='r15' and saved;return trace
        elif op=='movi':assert p[0]=='r0';value=int(p[1],0)
        elif op in ('bez','bnez'):
            assert p[0]=='r0'
            if (value==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='bsr':
            name=helpers[int(args,0)]
            if name=='trim':trace.append(['trim']);value=result
            else:trace.append(['set',value]);value=0xdeadbeef
        else:raise AssertionError((pc,op,args))
        pc=nxt
    raise AssertionError('execution bound')


def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x39c64','--stop-address=0x39c78',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-stage1-clock-initialize/initialize.disassembly.txt').read_text())
    helpers={0x38e48:'trim',0x397f4:'set'};mapped={a-0x38954+0x10000000:n for a,n in helpers.items()}
    results=[*range(256),0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    for result in results:
        expected=[['trim']]+([['set',1]] if result==0 else [])
        assert execute(old,0x39c64,helpers,result)==expected
        assert execute(new,0x10001310,mapped,result)==expected
    report={'cases':len(results),'build':evidence,'limits':['Decoded board-hook branch and argument comparison; trim and setter behavior modeled at call boundary. Hardware and full initialization composition pending.']}
    (ROOT/'docs/research/gx8002-stage1-board-clock.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'board clock cases passed')
