# SPDX-License-Identifier: MIT
"""Normalize decoded stock SRAM PCs to runtime addresses without changing ops."""
import subprocess
from verify_gx8002_padmux_get import build,programs
from verify_gx8002_memcpy_source import decode
from link_gx8002_uart_console import ROOT


def stock_code():
    build();programs()
    raw=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D',
        '--start-address=0x16a58','--stop-address=0x173e0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    result={};delta=0x1000dfec
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=' '+hex((int(parts[-1].strip(),0)+delta)&0xffffffff)
            args=','.join(parts).strip()
        result[pc+delta]=(op,args,width)
    return result
