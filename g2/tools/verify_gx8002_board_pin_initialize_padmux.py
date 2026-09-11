# SPDX-License-Identifier: MIT
"""Board initializer/padmux initializer decoded call-boundary composition."""
import json,subprocess
from itertools import product
import verify_gx8002_board_pin_initialize as board
import verify_gx8002_padmux_init as padmux
import verify_gx8002_padmux_set as setter


def verify():
    candidate=board.build();outers=board.programs()
    out=board.ROOT/'build/gx8002-board';pre=str(board.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=board.decode(subprocess.check_output([pre,'-D','--start-address=0xfbbc','--stop-address=0xfc0c',str(out/'padmux-get-stock.elf')],text=True))
    new=board.decode((out/'padmux-init-candidate.disassembly.txt').read_text());count=0
    table=[(p,int(p!=2)) for p in range(13)]
    old_set=board.decode(subprocess.check_output([pre,'-D','--start-address=0xfb68','--stop-address=0xfbbc',str(out/'padmux-get-stock.elf')],text=True))
    new_set=board.decode((out/'padmux-set-candidate.disassembly.txt').read_text())
    for outer,inner,leaf,result,returns,initial in product((0,1),(0,1),(0,1),(0,1,0xffffffff),(False,True),(0,0xffffffff)):
        calls=[];words={0xa0010090+i*4:initial for i in range(4)};writes=[]
        def hook(pointer,size):
            if (pointer,size)!=(board.TABLE,13):raise ValueError('Board padmux arguments')
            def set_hook(pin,function):
                address=0xa0010090+4*(pin//8);word=words[address]
                got=setter.execute(new_set if leaf else old_set,setter.ADDRESS if leaf else 0xfb68,pin,function,word,result)
                if got!=setter.expected(pin,function,word,result):raise ValueError('Board initializer setter behavior')
                for event in got[0]:
                    if event[0]=='write':words[event[1]]=event[2];writes.append(event)
                return got[1]
            observed=padmux.execute(new if inner else old,padmux.ADDRESS if inner else 0xfbbc,table,pointer,size,result,setter_hook=set_hook)
            if observed!=padmux.expected(table,pointer,size):raise ValueError('Board padmux initialization')
            sets=[event for event in observed[0] if event[0]=='set']
            if sets!=[('set',p,int(p<13 and p!=2)) for p in range(32)]:raise ValueError('Board default pin policy')
            calls.append(observed);return observed[1]
        observed=board.execute(outers[outer],board.ADDRESS if outer else 0xfe2c,table,0,returns,init_hook=hook)
        if observed!=board.expected(table,0,returns) or len(calls)!=1:raise ValueError('Board padmux composition')
        if words!={0xa0010090:0x11111011,0xa0010094:0x11111,0xa0010098:0,0xa001009c:0} or len(writes)!=32:
            raise ValueError('Board initializer final padmux policy')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded board/padmux initialization including 32-pin defaults and source board policy. Setters decoded against shared register words; setter checker and other board helpers modeled. Separate frames and no hardware proof.']}


if __name__=='__main__':
    report=verify();(board.ROOT/'docs/research/gx8002-board-pin-initialize-padmux.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board/padmux initialization combinations:',report['combinations'])
