#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Aligned receive replay, separate from receive qualification."""
import json,subprocess
from verify_gx8002_backup_spi_transfer_lifecycle import ROOT,build,programs,execute
from model_gx8002_backup_spi_transfer_rx import Case,expected

def verify():
    candidate=build();stock,source=programs()
    cases=[]
    for bits in (0,1,8,9,16,17,24,32):
        width=1 if bits<=8 else 2 if bits<=16 else 4
        for count in (0,1,2,3,17):
            for depth in (2,16):
                for delay in (False,True):
                    levels=[];remaining=count
                    while remaining:
                        chunk=min(remaining,depth)
                        if delay: levels.append(0)
                        levels.append(chunk);remaining-=chunk
                    cases.append(Case(bits=bits,length=width*count,rx_depth=depth,
                                      levels=tuple(levels),words=tuple((i*0x1020304+0xabcdef01)&0xffffffff for i in range(count))))
    for case in cases:
        execute(stock,case,expected)
        execute(source,case,expected)
    return {'candidate':candidate,'decoded_cases':len(cases),
            'source_admitted':False,'hardware_qualified':False,
            'limits':['RX cases only; multi-transfer and hardware qualification remain incomplete.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-backup-spi-transfer-rx.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RX cases:',report['decoded_cases'])
