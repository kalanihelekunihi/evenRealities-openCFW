# SPDX-License-Identifier: MIT
"""Board guard with decoded setter/checker/getter at modeled call boundaries."""
import json
import subprocess
from itertools import product
import verify_gx8002_board_pin_configure as guard
import verify_gx8002_padmux_set as setter
import verify_gx8002_padmux_check as check
import verify_gx8002_padmux_get as get


def verify():
    candidate=guard.build();setter.build();check.build();get.build()
    guards=guard.programs();getters=get.programs()
    out=get.ROOT/'build/gx8002-board'
    pre=str(get.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def stock(start,end):
        return get.decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(out/'padmux-get-stock.elf')],text=True))
    checks=(stock(0xfb44,0xfb68),get.decode((out/'padmux-check-candidate.disassembly.txt').read_text()))
    sets=(stock(0xfb68,0xfbbc),get.decode((out/'padmux-set-candidate.disassembly.txt').read_text()))
    count=0
    for g,s,c,l,pin,mode,initialized,word in product((0,1),(0,1),(0,1),(0,1),
            (0,2,3,32,33,0x80000000,0xffffffff),(0,3,16,255,0xffffffff),
            (0,1),(0,0xffffffff,0x12345678)):
        calls=[]
        def checker(p,f,observed):
            def getter(p):
                result=get.execute(getters[l],get.ADDRESS if l else 0xfb18,p,observed)
                if result!=get.expected(p,observed):raise ValueError('Guard getter mismatch')
                calls.extend(('read',*row) for row in result[0])
                return result[1]
            result=check.execute(checks[c],check.ADDRESS if c else 0xfb44,p,f,0,getter_hook=getter)
            oracle=get.expected(p,observed)[1]
            if result!=check.expected(p,f,oracle):raise ValueError('Guard checker mismatch')
            return result[1]
        def set_hook(p,f):
            def readback(p,f,written):return checker(p,f,written)
            result=setter.execute(sets[s],setter.ADDRESS if s else 0xfb68,p,f,word,0,check_hook=readback)
            calls.append(('set-result',result))
            if pin<=32:
                ret=0 if mode==(mode&15) else guard.MASK
            else:ret=guard.MASK
            if result!=setter.expected(pin,mode,word,ret):raise ValueError('Guard setter mismatch')
            return result[1]
        result=guard.execute(guards[g],guard.ADDRESS if g else 0xfd68,pin,mode,initialized,0,0,37,
                             check_hook=lambda p,f:checker(p,f,word),set_hook=set_hook)
        expected_check=check.expected(pin,int(pin!=2),get.expected(pin,word)[1])[1]
        if result!=guard.expected(pin,mode,initialized,expected_check):raise ValueError('Guard composed mismatch')
        should_set=bool(initialized or expected_check==0)
        if sum(row[0]=='set-result' for row in calls)!=int(should_set):raise ValueError('Guard setter call count')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['All 16 stock/source guard/set/check/get combinations, modeled written readback. Separate checked helper frames; no shared nested stack, concurrency or physical pad proof. Diagnostic output remains modeled.']}


if __name__=='__main__':
    report=verify()
    (get.ROOT/'docs/research/gx8002-board-pin-padmux-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board guard/padmux combinations:',report['combinations'])
