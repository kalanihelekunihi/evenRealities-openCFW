#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Aligned transmit replay, separate from receive qualification."""
import json,subprocess
from verify_gx8002_spi_transfer_lifecycle import ROOT,build,analyze,decode,execute
from model_gx8002_spi_transfer_tx import Case,expected

def verify():
    attribution=analyze();candidate=build();out=ROOT/'build/gx8002-board'
    stock=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(out/'dw-spi-quick-transfer-oracle.elf')],text=True))
    source=decode((out/'dw-spi-quick-transfer-candidate.disassembly.txt').read_text())
    cases=[]
    for bits in (0,1,8,9,16,17,24,32):
        width=1 if bits<=8 else 2 if bits<=16 else 4
        for count in (0,1,2,3,17):
            for depth in (2,16):
                for delay in (False,True):
                    levels=[];remaining=count
                    while remaining:
                        if delay: levels.append(depth)
                        levels.append(0);remaining-=min(remaining,depth)
                    cases.append(Case(bits=bits,length=width*count,tx_depth=depth,
                                      levels=tuple(levels),status=(0,4,1,0) if delay else (4,0),
                                      data=bytes((i*17+93)&255 for i in range(width*count))))
    for case in cases:
        execute(stock,case,expected)
        execute(source,case,expected)
    return {'candidate':candidate,'attribution':attribution,'decoded_cases':len(cases),
            'source_admitted':False,'hardware_qualified':False,
            'limits':['TX cases only; RX, multi-transfer and hardware qualification remain incomplete.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-spi-transfer-tx-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('TX cases:',report['decoded_cases'])
