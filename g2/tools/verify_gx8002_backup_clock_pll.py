# SPDX-License-Identifier: MIT
"""Compare complete backup PLL configuration and bounded waiting paths."""
import json,random,subprocess
from itertools import product
from build_gx8002_backup_clock_pll import build,ROOT,Elf32,sha
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA
from execute_gx8002_clock_pll_wait import execute
from verify_gx8002_clock_pll import oracle,BASE,OFFSETS
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3c334','--stop-address=0x3c528',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-clock-pll/pll.disassembly.txt').read_text())
    rng=random.Random(0x3c334);cases=0
    scenarios=[(0,[8],[100]),(1,[0,8],[100,1100]),(1,[0],[100,1101]),(0xffffffff,[0],[0,0x100000000]),(0x20000000,[0,8],[0xfffffffffffffff0,0x10])]
    for blocking,enabled,pattern in product((False,True),(0,1,2,0xffffffff),range(16)):
        fields=[rng.getrandbits(32) for _ in range(14)];fields[0]=enabled
        registers={o:rng.getrandbits(32) for o in OFFSETS}
        for timeout,locks,times in scenarios:
            if blocking:locks=[0,0,8];times=[]
            options={'fields':fields,'registers':{BASE+o:v for o,v in registers.items()},'time_address':0x10005070}
            a=execute(old,0x3c448 if blocking else 0x3c334,enabled,timeout,enabled,locks,times,stock_delta=0x10003000-0x3b940,**options)
            b=execute(new,0x10003b08 if blocking else 0x100039f4,enabled,timeout,enabled,locks,times,**options)
            assert a==b,(blocking,enabled,timeout,a,b)
            config=[e for e in b[2] if e[0] in ('read','write') and e[1] in options['registers']]
            assert config==oracle(True,fields,registers,0)[0]
            assert b[0]=='return'
            if not blocking:
                wanted=0
                if enabled==1:
                    sample=1
                    for lock in locks:
                        if lock&8:break
                        elapsed=(times[sample]-times[0])&0xffffffffffffffff;sample+=1
                        if elapsed>((timeout*1000)&0xffffffff):wanted=0xffffffff;break
                assert b[1]==wanted
            cases+=1
    report={'cases':cases,'candidate':evidence,'limits':['Complete decoded configuration/wait bodies, independent ordered configuration oracle and scripted timeout return expectations. Non-null immutable PLL fields; modeled microsecond time and finite lock sequences. Physical PLL, concurrent mutation and nonterminating waits unqualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-pll-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'PLL cases passed')
