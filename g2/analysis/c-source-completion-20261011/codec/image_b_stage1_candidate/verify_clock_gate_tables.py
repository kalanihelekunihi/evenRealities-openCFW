#!/usr/bin/env python3
"""Compare pinned GX8002 clock descriptor source with BINH-B stage1 data."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
STOCK = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage1.bin'
TOOL = ROOT / 'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
OBJECT = HERE / 'build/backup_stage1_clock_gate.o'
OUT = HERE / 'build'
SECTIONS = {'param': '.data.gx_clock_param_table',
            'dto': '.data.gx_clock_dto_table',
            'div': '.data.gx_clock_div_table',
            'sources': '.data.gx_stage1_sources'}


def target(tool, *args):
    cmd = ['docker', 'run', '--rm', '--network=none', '--read-only',
           '--platform', 'linux/amd64',
           '--mount', f'type=bind,src={TOOL},dst=/tool,readonly',
           '--mount', f'type=bind,src={OUT},dst=/out',
           'opencfw/iar-base:10.10.2-local', f'/tool/bin/csky-abiv2-elf-{tool}', *args]
    return subprocess.check_output(cmd, text=True)


def main():
    stock = STOCK.read_bytes()
    outputs = {name: OUT / f'clock_{name}.bin' for name in SECTIONS}
    args = []
    for name, section in SECTIONS.items():
        args.extend(['--dump-section', f'{section}=/out/{outputs[name].name}'])
    target('objcopy', *args, '/out/backup_stage1_clock_gate.o', '/out/clock_copy.o')
    data = {name: path.read_bytes() for name, path in outputs.items()}
    assert len(data['param']) == 0x1a0 and len(data['dto']) == 3 and len(data['div']) == 0x44
    assert len(data['sources']) == 80
    assert data['sources'] == stock[0x16a0:0x16f0]
    assert data['dto'] == stock[0x16f0:0x16f3]
    assert data['div'] == stock[0x16f4:0x1738]
    for i in range(26):
        assert data['param'][i*16:i*16+8] == stock[0x14e0+i*16:0x14e0+i*16+8]
    listing = target('readelf', '-r', '/out/backup_stage1_clock_gate.o')
    match = re.search(r"Relocation section '\.rela\.data\.gx_clock_param_table'.*?(?=Relocation section|\Z)", listing, re.S)
    assert match
    relocated = {}
    for line in match.group(0).splitlines():
        parts = line.split()
        if len(parts) < 6 or not re.fullmatch(r'[0-9a-f]{8}', parts[0]):
            continue
        off = int(parts[0], 16)
        section = parts[4]
        addend = int(parts[6], 16) if len(parts) > 6 else 0
        if 'clock_div' in section:
            value = 0x200016dc + addend
        elif 'clock_dto' in section:
            value = 0x200016d8 + addend
        else:
            raise AssertionError(section)
        relocated[off] = value
    assert len(relocated) == 20
    for i in range(26):
        for off in (i*16+8, i*16+12):
            native = int.from_bytes(stock[0x14e0+off:0x14e4+off], 'little')
            assert native == relocated.get(off, 0), (hex(off),hex(native),hex(relocated.get(off,0)))
    receipt = {'result': 'PASS',
               'stock_sha256': hashlib.sha256(stock).hexdigest(),
               'object_sha256': hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
               'parameter_records': 26, 'parameter_nonpointer_bytes': 26*8,
               'pointer_relocations': len(relocated),
               'dto_bytes': 3, 'divider_bytes': 68, 'source_records': 10,
               'stock_runtime_vmas': {'param':'0x200014c8', 'sources':'0x20001688', 'dto':'0x200016d8', 'div':'0x200016dc'},
               'stock_load_offsets': {'param':'0x14e0', 'sources':'0x16a0', 'dto':'0x16f0', 'div':'0x16f4'},
               'limits': ['Table fields and relocations match stock; executable dispatcher effects and final stage1 placement still require qualification.']}
    out = HERE / 'clock-gate-tables-receipt.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(out)

if __name__ == '__main__':
    main()
