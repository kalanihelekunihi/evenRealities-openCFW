# SPDX-License-Identifier: MIT
"""Decoded fatal cleanup writes preserve other pin fields in shared words."""
import json,subprocess
from itertools import product
import verify_gx8002_board_pin_setup as setup
import verify_gx8002_padmux_set as setter
import verify_gx8002_padmux_check as checker
import verify_gx8002_padmux_get as getter
from verify_gx8002_memcpy_source import decode


def verify():
    candidate=setup.build();outers=setup.programs()
    out=setup.ROOT/'build/gx8002-board';pre=str(setup.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfb68','--stop-address=0xfbbc',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'padmux-set-candidate.disassembly.txt').read_text());count=0
    old_check=decode(subprocess.check_output([pre,'-D','--start-address=0xfb44','--stop-address=0xfb68',str(out/'padmux-get-stock.elf')],text=True))
    new_check=decode((out/'padmux-check-candidate.disassembly.txt').read_text())
    getters=getter.programs()
    for outer,inner,middle,leaf,failed,word,inverted in product((0,1),(0,1),(0,1),(0,1),(False,True),(0,0xffffffff,0x12345678),(False,True)):
        words={0xa0010090:word,0xa0010094:word};writes=[]
        def hook(pin,mode):
            address=0xa0010090+4*(pin//8);previous=words[address]
            check_result=setup.MASK if inverted else 0
            def check_hook(p,f,written):
                observed=written^setup.MASK if inverted else written
                def get_hook(p):
                    got=getter.execute(getters[leaf],getter.ADDRESS if leaf else 0xfb18,p,observed)
                    if got!=getter.expected(p,observed):raise ValueError('Cleanup getter mismatch')
                    return got[1]
                checked=checker.execute(new_check if middle else old_check,checker.ADDRESS if middle else 0xfb44,p,f,0,getter_hook=get_hook)
                if checked!=checker.expected(p,f,getter.expected(p,observed)[1]):raise ValueError('Cleanup checker mismatch')
                return checked[1]
            result=setter.execute(new if inner else old,setter.ADDRESS if inner else 0xfb68,pin,mode,previous,0,check_hook=check_hook)
            if result!=setter.expected(pin,mode,previous,check_result):raise ValueError('Cleanup setter mismatch')
            for event in result[0]:
                if event[0]=='write':words[event[1]]=event[2];writes.append(event)
            return result[1]
        results=[setup.MASK if failed else 0]+[0]*7
        observed=setup.execute(outers[outer],setup.ADDRESS if outer else 0xfda8,results,set_hook=hook)
        if observed!=setup.expected(results):raise ValueError('Cleanup outer mismatch')
        want={0xa0010090:word,0xa0010094:word};expected_writes=[]
        if failed:
            for pin in (5,6,11,12):
                address=0xa0010090+4*(pin//8)
                want[address]&=~(15<<(4*(pin%8)))
                expected_writes.append(('write',address,want[address]))
        if words!=want or writes!=expected_writes:raise ValueError('Cleanup shared register fields')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded setup/setter/checker/getter with shared cleanup words and written/inverted readback. Guard and printf calls modeled. Separate frames; no hardware proof.']}


if __name__=='__main__':
    report=verify();(setup.ROOT/'docs/research/gx8002-board-pin-setup-cleanup.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Setup cleanup combinations:',report['combinations'])
