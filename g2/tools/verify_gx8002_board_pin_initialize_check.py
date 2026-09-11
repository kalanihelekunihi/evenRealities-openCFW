# SPDX-License-Identifier: MIT
"""Initializer pin checking composed with decoded padmux reads."""
import json,subprocess
from itertools import product
import verify_gx8002_board_pin_initialize as init
import verify_gx8002_padmux_check as check
import verify_gx8002_padmux_get as get


def verify():
    candidate=init.build();outers=init.programs();getters=get.programs()
    out=init.ROOT/'build/gx8002-board';pre=str(init.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=init.decode(subprocess.check_output([pre,'-D','--start-address=0xfb44','--stop-address=0xfb68',str(out/'padmux-get-stock.elf')],text=True))
    new=init.decode((out/'padmux-check-candidate.disassembly.txt').read_text());count=0
    table=[(p,int(p!=2)) for p in range(13)]
    for outer,middle,leaf,word in product((0,1),(0,1),(0,1),(0,0xffffffff,0x11111011,0x12345678)):
        reads=[];errors=0
        for pin,function in table:
            observed=(word>>(4*(pin%8)))&15
            if observed!=function:errors|=1<<pin
        def hook(pin,function):
            def getter(p):
                result=get.execute(getters[leaf],get.ADDRESS if leaf else 0xfb18,p,word)
                if result!=get.expected(p,word):raise ValueError('Initializer getter')
                reads.extend(result[0]);return result[1]
            result=check.execute(new if middle else old,check.ADDRESS if middle else 0xfb44,pin,function,0,getter_hook=getter)
            if result!=check.expected(pin,function,get.expected(pin,word)[1]):raise ValueError('Initializer checker')
            return result[1]
        result=init.execute(outers[outer],init.ADDRESS if outer else 0xfe2c,table,0,check_hook=hook)
        if result!=init.expected(table,errors,True):raise ValueError('Initializer checker branches')
        if reads!=[(0xa0010090+4*(p//8),word) for p in range(13)]:raise ValueError('Initializer read order')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded initializer/checker/getter; scripted post-init padmux words. Other helpers modeled; separate frames and no physical hardware proof.']}


if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-board-pin-initialize-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer/check/get combinations:',report['combinations'])
