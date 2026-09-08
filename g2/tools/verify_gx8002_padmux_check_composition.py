#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded checker/getter call-boundary composition."""
import json,subprocess
from itertools import product
import verify_gx8002_padmux_check as check
import verify_gx8002_padmux_get as get


def verify():
    candidate=check.build();getter=get.build()
    old_get,new_get=get.programs()
    out=get.ROOT/'build/gx8002-board'
    prefix=str(get.ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=check.decode(subprocess.check_output([prefix,'-D','--start-address=0xfb44','--stop-address=0xfb68',str(out/'padmux-get-stock.elf')],text=True))
    new=check.decode((out/'padmux-check-candidate.disassembly.txt').read_text())
    count=calls=0
    for outer,leaf,pin,function,word in product((0,1),(0,1),(*range(34),0x80000000,0xffffffff),
                                              (0,1,15,16,255,0x80000000),(0,0xffffffff,0x12345678)):
        wanted_reads,wanted_value=get.expected(pin,word)
        observed=[]
        def hook(argument):
            nonlocal calls
            reads,value=get.execute(new_get if leaf else old_get,get.ADDRESS if leaf else 0xfb18,argument,word)
            if (reads,value)!=(wanted_reads,wanted_value): raise ValueError('Composed getter mismatch')
            observed.extend(reads);calls+=1
            return value
        result=check.execute(new if outer else old,check.ADDRESS if outer else 0xfb44,pin,function,0,getter_hook=hook)
        if result!=check.expected(pin,function,wanted_value): raise ValueError('Composed check mismatch')
        if observed!=([] if pin&0x80000000 or function&0x80000000 else wanted_reads):
            raise ValueError('Unexpected composed MMIO')
        count+=1
    return {'candidate':candidate,'getter':getter,'combinations':count,'getter_calls':calls,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Call-boundary composition with independently checked getter leaf ABI and caller clobbers; no hardware pad effects or concurrency proof.']}

if __name__=='__main__':
    report=verify()
    (get.ROOT/'docs/research/gx8002-padmux-check-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Checker/getter combinations:',report['combinations'])
