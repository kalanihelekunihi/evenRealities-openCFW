#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compose decoded setter, checker, and getter with explicit readback state."""
import json,subprocess
from itertools import product
import verify_gx8002_padmux_set as setter
import verify_gx8002_padmux_check as check
import verify_gx8002_padmux_get as get


def verify():
    candidate=setter.build();checker=check.build();getter=get.build()
    old_get,new_get=get.programs();out=get.ROOT/'build/gx8002-board'
    pre=str(get.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def stock(start,end):
        return get.decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(out/'padmux-get-stock.elf')],text=True))
    old_check=stock(0xfb44,0xfb68);old_set=stock(0xfb68,0xfbbc)
    new_check=get.decode((out/'padmux-check-candidate.disassembly.txt').read_text())
    new_set=get.decode((out/'padmux-set-candidate.disassembly.txt').read_text())
    count=check_calls=get_calls=0
    for outer,middle,leaf,pin,function,word,readback in product((0,1),(0,1),(0,1),
            (*range(34),0x80000000,0xffffffff),(0,1,15,16,255,0x80000000,0xffffffff),
            (0,0xffffffff,0x12345678),('written','inverted')):
        seen=[]
        shift=4*(pin%8)
        written=(word&~(15<<shift))|((function&15)<<shift)
        observed_word=written if readback=='written' else written^0xffffffff
        def checker_hook(argument,mode,actual_word):
            nonlocal check_calls
            check_calls+=1
            if (argument,mode,actual_word)!=(pin,function,written): raise ValueError('Setter boundary mismatch')
            def getter_hook(get_pin):
                nonlocal get_calls
                get_calls+=1
                result=get.execute(new_get if leaf else old_get,get.ADDRESS if leaf else 0xfb18,get_pin,observed_word)
                if result!=get.expected(pin,observed_word): raise ValueError('Readback getter mismatch')
                seen.extend(result[0]);return result[1]
            result=check.execute(new_check if middle else old_check,check.ADDRESS if middle else 0xfb44,
                                 argument,mode,0,getter_hook=getter_hook)
            if result!=check.expected(pin,function,(observed_word>>shift)&15): raise ValueError('Readback checker mismatch')
            return result[1]
        result=setter.execute(new_set if outer else old_set,setter.ADDRESS if outer else 0xfb68,
                              pin,function,word,0,check_hook=checker_hook)
        helper_result=0 if function==((observed_word>>shift)&15) else 0xffffffff
        if result!=setter.expected(pin,function,word,helper_result): raise ValueError('Composed setter mismatch')
        expected_reads=[] if pin>32 or function&0x80000000 else [(0xa0010090+4*(pin//8),observed_word)]
        if seen!=expected_reads: raise ValueError('Composed readback trace mismatch')
        count+=1
    return {'candidate':candidate,'checker':checker,'getter':getter,'combinations':count,
            'checker_calls':check_calls,'getter_calls':get_calls,'source_admitted':False,'hardware_qualified':False,
            'limits':['All eight stock/C call-boundary combinations; written and inverted readback states. Helpers use independent checked ABI stacks. No physical pad effect, shared nested stack, or concurrent access proof.']}

if __name__=='__main__':
    report=verify()
    (get.ROOT/'docs/research/gx8002-padmux-set-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Setter/checker/getter combinations:',report['combinations'])
