#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Scoped alignment-error replay; no FIFO transfer admission."""
import json,subprocess
from itertools import product
from verify_gx8002_backup_spi_transfer_lifecycle import execute,ROOT,build,programs
from model_gx8002_backup_spi_transfer_alignment import Case,expected


def verify():
    candidate=build();stock,source=programs()
    count=0
    for bits,length,buffer,tx,divider in product((9,16,17,24,32),(1,3,4,7),(0x20030000,0x20030001),(False,True),(0,1,10,0x10001)):
        case=Case(bits,length,buffer,tx,divider=divider)
        width=2 if bits<=16 else 4
        if not length%width and not buffer%width: continue
        execute(stock,case,expected);execute(source,case,expected);count+=1
    return {'candidate':candidate,'decoded_cases':count,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Misaligned length/buffer setup and error shutdown only; no FIFO execution or complete-function admission.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-backup-spi-transfer-alignment.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Alignment cases:',report['decoded_cases'])
