# SPDX-License-Identifier: MIT
"""Initializer/GPIO direction composition with shared MMIO words."""
import json
from itertools import product
import verify_gx8002_board_pin_initialize as init
import verify_gx8002_gpio_output as gpio


def verify():
    candidate=init.build();outers=init.programs();leaves=gpio.programs();count=0
    for outer,leaf,word,errors in product((0,1),(0,1),(0,0xffffffff,0x12345678),(0,8191)):
        table=[(p,int(p!=2)) for p in range(13)]
        words={0xa0001000:word,0xa0001004:word,0xa0001008:word};trace=[]
        def hook(pin,direction):
            nonlocal words
            result=gpio.execute(leaves[leaf],0x10205f24 if leaf else 0xf4b0,pin,direction,words,804)
            if result!=gpio.expected('direction',pin,direction,words):raise ValueError('Initializer GPIO leaf mismatch')
            trace.extend(result[0]);words=result[1];return result[2]
        result=init.execute(outers[outer],init.ADDRESS if outer else 0xfe2c,table,errors,direction_hook=hook)
        if result!=init.expected(table,errors,True):raise ValueError('Initializer GPIO calls')
        if words!={0xa0001000:word&~8191,0xa0001004:word,0xa0001008:word|8191} or len(trace)!=52:
            raise ValueError('Initializer GPIO shared state')
        count+=1
    return {'candidate':candidate,'combinations':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded initializer/GPIO direction with shared scripted register words. Other helpers modeled, separate frames; physical pin behavior not qualified.']}


if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-board-pin-initialize-gpio.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer/GPIO combinations:',report['combinations'])
