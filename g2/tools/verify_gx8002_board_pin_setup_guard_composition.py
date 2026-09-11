# SPDX-License-Identifier: MIT
"""Decoded setup/guard call-boundary composition with per-pin conflict models."""
import json
from itertools import product
import verify_gx8002_board_pin_setup as setup
import verify_gx8002_board_pin_configure as guard


def verify():
    candidate=setup.build();outers=setup.programs();inners=guard.programs();count=0
    for outer,inner,initialized,failures in product((0,1),(0,1),(0,1),range(256)):
        results=[];calls=[]
        def hook(pin,mode):
            index=len(results)
            if (pin,mode)!=setup.PINS[index]:raise ValueError('Setup guard argument order')
            check_result=guard.MASK if failures&(1<<index) else 0
            result=guard.execute(inners[inner],guard.ADDRESS if inner else 0xfd68,
                                 pin,mode,initialized,check_result,guard.MASK,37)
            if result!=guard.expected(pin,mode,initialized,check_result):raise ValueError('Setup guard behavior')
            calls.append(result[0]);results.append(result[1]);return result[1]
        observed=setup.execute(outers[outer],setup.ADDRESS if outer else 0xfda8,[0]*8,
                               set_result=setup.MASK,printf_result=37,configure_hook=hook)
        if observed!=setup.expected(results) or len(calls)!=8:raise ValueError('Setup composed sequence')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['All stock/source setup/guard combinations and conflict masks. Separate checked frames; guard padmux/printf and setup cleanup calls modeled here. Physical hardware not qualified.']}


if __name__=='__main__':
    report=verify();(setup.ROOT/'docs/research/gx8002-board-pin-setup-guard-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Setup/guard combinations:',report['combinations'])
