#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode IRQ reads without assigning unproven meanings to low addresses."""
import hashlib
import json
import re
import struct
import shutil
from verify_gx8002_logging import check_paths
import subprocess
from itertools import product
from build_gx8002_dw_spi_irq_candidate import ROOT, IMAGE, build
from verify_gx8002_memcpy_source import decode

MASK = 0xffffffff
ADDRESS = 0x10206170
CONTEXT = 0x2002b000
REGISTERS = 0xa0002000


def expected(status, low38, low3c):
    trace = [(CONTEXT+4, REGISTERS), (REGISTERS+0x30, status)]
    if status & 2:
        trace.append((0x38, low38))
    if status & 8:
        trace.append((0x3c, low3c))
    return trace, 0


def execute(code, entry, status, low38, low3c, seed):
    memory = {CONTEXT+4: REGISTERS, REGISTERS+0x30: status, 0x38: low38, 0x3c: low3c}
    r = {f'r{i}': (seed+i*0x1020304)&MASK for i in range(32)}
    r['r1'] = CONTEXT
    initial = r.copy()
    trace = []
    pc = entry
    for _ in range(30):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc+width
        if op == 'ld.w':
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match:
                raise ValueError('IRQ load operand')
            reg,base,offset = match.groups()
            address = (r[base]+int(offset,0))&MASK
            if address not in memory:
                raise ValueError('Unexpected IRQ read address')
            r[reg] = memory[address]
            trace.append((address,r[reg]))
        elif op in ('movi','lrw'):
            r[p[0]] = int(p[1],0)&MASK
        elif op == 'andi':
            r[p[0]] = r[p[1]]&int(p[2],0)
        elif op == 'bez':
            if r[p[0]] == 0:
                nxt = int(p[1],0)
        elif op == 'rts':
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('IRQ leaf ABI')
            return trace,r['r0']
        else:
            raise ValueError('Unhandled IRQ instruction '+op)
        pc = nxt
    raise ValueError('IRQ execution bound')


def programs():
    out = ROOT/'build/gx8002-board'
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    path = out/'dw-spi-irq-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(path)],check=True)
    data = bytearray(path.read_bytes())
    struct.pack_into('<I',data,36,0x21006009)
    path.write_bytes(data)
    stock = decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf6fc','--stop-address=0xf71c',str(path)],text=True))
    source = decode((out/'dw-spi-irq-candidate.disassembly.txt').read_text())
    return stock, source


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate = build()
    stock, source = programs()
    count = 0
    for status,low38,low3c,seed in product((*range(256),0x80000000,MASK),
                                         (0,MASK,0x12345678),(0,MASK,0xabcdef01),(0,MASK)):
        want = expected(status,low38,low3c)
        if execute(stock,0xf6fc,status,low38,low3c,seed)!=want or execute(source,ADDRESS,status,low38,low3c,seed)!=want:
            raise ValueError('IRQ read-sequence mismatch')
        count += 1
    hashes = {name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest()
              for name in ('verify_gx8002_dw_spi_irq.py','build_gx8002_dw_spi_irq_candidate.py')}
    if not candidate['fits']:
        raise ValueError('IRQ candidate exceeds slot')
    row = {k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences'] = [{'symbol':candidate['symbol'],'package_offset':0xf6fc,
                                'bytes':32,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/dw-spi-irq-candidate.elf',output/'dw-spi-irq.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'evidence_sha256':hashes,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Low-address diagnostic threshold explicitly configured for this candidate.',
                      'Read order, condition masks, return and leaf ABI verified; low-address mapping and hardware effects unresolved.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-dw-spi-irq-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded cases:',report['decoded_cases'])
