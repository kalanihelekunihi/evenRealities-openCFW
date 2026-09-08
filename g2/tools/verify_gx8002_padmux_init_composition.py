#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded initializer/setter composition with persistent register words."""
import json,subprocess
from itertools import product
import verify_gx8002_padmux_init as init
import verify_gx8002_padmux_set as setter
import verify_gx8002_padmux_check as check
import verify_gx8002_padmux_get as get
from verify_gx8002_padmux_get import build as build_getter,programs


def verify():
    candidate=init.build();set_candidate=setter.build();check_candidate=check.build();build_getter();old_get,new_get=programs()
    out=init.ROOT/'build/gx8002-board';pre=str(init.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def stock(start,end):
        return init.decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(out/'padmux-get-stock.elf')],text=True))
    old=stock(0xfbbc,0xfc0c);old_set=stock(0xfb68,0xfbbc)
    new=init.decode((out/'padmux-init-candidate.disassembly.txt').read_text())
    new_set=init.decode((out/'padmux-set-candidate.disassembly.txt').read_text())
    old_check=stock(0xfb44,0xfb68)
    new_check=init.decode((out/'padmux-check-candidate.disassembly.txt').read_text())
    tables=([],[(i,(i*3)%16) for i in range(32)],[(i,255-i) for i in reversed(range(32))],[(3,9),(3,2),(32,5),(255,7)])
    count=calls=0
    for outer,leaf,middle,last,entries,initial,invert in product((0,1),(0,1),(0,1),(0,1),tables,(0,0xffffffff,0x12345678),(False,True)):
        words=[initial]*4;expected_words=words.copy()
        def hook(pin,function):
            nonlocal calls
            index=pin//8;before=words[index]
            shift=4*(pin%8)
            written=(before&~(15<<shift))|((function&15)<<shift)
            readback=written^(0xffffffff if invert else 0)
            check_result=0 if function==((readback>>shift)&15) else 0xffffffff
            def check_hook(argument,mode,actual_word):
                if (argument,mode,actual_word)!=(pin,function,written):raise ValueError('Initializer chain boundary')
                def get_hook(argument):
                    reads,value=get.execute(new_get if last else old_get,get.ADDRESS if last else 0xfb18,argument,readback)
                    if (reads,value)!=get.expected(pin,readback):raise ValueError('Initializer chain getter')
                    return value
                observed=check.execute(new_check if middle else old_check,check.ADDRESS if middle else 0xfb44,pin,function,0,getter_hook=get_hook)
                if observed!=check.expected(pin,function,(readback>>shift)&15):raise ValueError('Initializer chain checker')
                return observed[1]
            trace,result=setter.execute(new_set if leaf else old_set,setter.ADDRESS if leaf else 0xfb68,pin,function,before,0,check_hook=check_hook)
            if (trace,result)!=setter.expected(pin,function,before,check_result):raise ValueError('Composed setter mismatch')
            writes=[x for x in trace if x[0]=='write']
            if len(writes)!=1:raise ValueError('Missing setter write')
            words[index]=writes[0][2];calls+=1
            return result
        result=init.execute(new if outer else old,init.ADDRESS if outer else 0xfbbc,entries,setter_hook=hook)
        if result!=init.expected(entries):raise ValueError('Composed initializer mismatch')
        for pin in range(32):
            function=next((f for p,f in entries if p==pin),0)
            shift=4*(pin%8);index=pin//8
            expected_words[index]=(expected_words[index]&~(15<<shift))|((function&15)<<shift)
        if words!=expected_words:raise ValueError('Persistent register state mismatch')
        count+=1
    return {'candidate':candidate,'setter':set_candidate,'checker':check_candidate,'combinations':count,'setter_calls':calls,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['All sixteen stock/C initializer/setter/checker/getter call-boundary combinations with persistent MMIO writes and written/inverted readback. Separate helper stacks; no physical effects or concurrency proof.']}

if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-padmux-init-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer/setter combinations:',report['combinations'],'calls:',report['setter_calls'])
