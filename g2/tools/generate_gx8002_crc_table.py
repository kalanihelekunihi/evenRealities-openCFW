#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the reflected CRC-32 table mathematically, then compare stock."""
import json
import struct
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
ROOT=Path(__file__).resolve().parents[1]


def table_values():
    values=[]
    for byte in range(256):
        remainder=byte
        for _ in range(8):
            remainder=(remainder>>1) ^ (0xedb88320 if remainder&1 else 0)
        values.append(remainder)
    return values


def generate(output):
    values=table_values()
    payload=struct.pack('<256I',*values)
    output.mkdir(parents=True,exist_ok=True)
    source='/* SPDX-License-Identifier: MIT */\n/* Generated from reflected polynomial 0xEDB88320; not extracted bytes. */\n#include <stdint.h>\nconst uint32_t open_cfw_gx8002_crc_table[256] = {\n'
    source+=''.join('    '+', '.join(f'0x{x:08x}U' for x in values[i:i+8])+',\n' for i in range(0,256,8))+'};\n'
    (output/'crc_table.c').write_text(source)
    # Stock is an oracle only, read after the complete output is generated.
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    offsets=[];start=0
    while True:
        offset=stock.find(payload,start)
        if offset<0:break
        offsets.append(offset);start=offset+1
    expected=0x1020b908-0x101f6a74
    if expected not in offsets:raise ValueError('UART CRC table mapping no longer matches')
    report={'generator_sha256':sha(Path(__file__).read_bytes()),'polynomial':'0xedb88320',
            'entries':256,'bytes_per_occurrence':len(payload),'payload_sha256':sha(payload),
            'source_sha256':sha(source.encode()),'stock_package_offsets':[hex(x) for x in offsets],
            'uart_crc_table_package_offset':hex(expected),'source_admitted':False,
            'limits':['Table identity only; CRC executable and placement require separate qualification.']}
    (output/'table-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(generate(ROOT/'build/gx8002-crc-table'),indent=2))
