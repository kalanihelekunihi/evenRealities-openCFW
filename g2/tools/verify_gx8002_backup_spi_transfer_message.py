#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Mixed-transfer message replay; still no hardware qualification."""
import json,subprocess
from dataclasses import replace
from itertools import product
from verify_gx8002_backup_spi_transfer_lifecycle import ROOT,build,programs,execute
from model_gx8002_backup_spi_transfer_message import Case,expected,TXCase,RXCase
from model_gx8002_backup_spi_transfer_alignment import Case as ErrorCase


def verify():
    candidate=build();stock,source=programs()
    variants=(TXCase(bits=8),TXCase(bits=32),RXCase(bits=16),RXCase(bits=32,length=8),
              TXCase(length=0,levels=(),data=b''),ErrorCase())
    count=0
    for length in (2,3):
        for transfers in product(variants,repeat=length):
            case=Case(tuple(replace(t,buffer=0x20030000+i*0x1000) for i,t in enumerate(transfers)))
            execute(stock,case,expected);execute(source,case,expected);count+=1
    for rx_bits,rx_width in ((8,1),(16,2),(32,4)):
        for tx_bits,tx_width in ((8,1),(16,2),(32,4)):
            for offset in (0,4):
                rx=RXCase(bits=rx_bits,length=8,levels=(8//rx_width,),words=tuple(0x12345678+i for i in range(8//rx_width)))
                tx=TXCase(bits=tx_bits,length=8,buffer=0x20030000+offset,data=bytes(range(8)))
                case=Case((rx,tx),shared_buffers=True)
                execute(stock,case,expected);execute(source,case,expected);count+=1
    return {'candidate':candidate,'decoded_cases':count,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Model composition for fixed distinct list nodes; clock helper does not mutate state. Invalid widths, concurrency and physical FIFO behavior remain unqualified.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-backup-spi-transfer-message.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Message cases:',report['decoded_cases'])
