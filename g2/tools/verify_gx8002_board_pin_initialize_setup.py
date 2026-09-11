# SPDX-License-Identifier: MIT
"""Decoded initializer/setup terminal-path composition."""
import json
from itertools import product
import verify_gx8002_board_pin_initialize as init
import verify_gx8002_board_pin_setup as setup


def verify():
    candidate=init.build();setup.build();outers=init.programs();inners=setup.programs()
    table=[(p,int(p!=2)) for p in range(13)];count=0
    for outer,inner,errors,failures in product((0,1),(0,1),(0,8191),range(256)):
        results=[setup.MASK if failures&(1<<i) else 0 for i in range(8)];seen=[]
        def hook():
            result=setup.execute(inners[inner],setup.ADDRESS if inner else 0xfda8,results,set_result=setup.MASK,printf_result=37)
            if result!=setup.expected(results):raise ValueError('Initializer setup body')
            seen.append(result);return result[0]=='returned'
        result=init.execute(outers[outer],init.ADDRESS if outer else 0xfe2c,table,errors,True,setup_hook=hook)
        if result!=init.expected(table,errors,failures==0) or len(seen)!=1:raise ValueError('Initializer setup completion flag')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded initializer/setup with separate saved-register frames. Setup guard/cleanup/printf returns and initializer helpers modeled. Terminal self-loop prevents flag write; physical hardware not qualified.']}


if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-board-pin-initialize-setup.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer/setup combinations:',report['combinations'])
