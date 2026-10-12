#!/usr/bin/env python3
"""Inventory aligned image-B stage2 initialized words that address its load span."""
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
STOCK = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
BASE = 0x10003000
END = 0x1001708c
SPANS = {
    'clock_uart_records': (0x100168c0, 0x10016c84),
    'audio_root_callbacks_state': (0x10016c84, 0x10016d60),
    'flash_descriptor_callbacks_profiles': (0x10016d60, 0x10016f60),
    'normal_initialized_tail': (0x10016f60, END),
}

def main():
    data = STOCK.read_bytes()
    assert len(data) == END - BASE
    rows = []
    for address in range(0x100168c0, END, 4):
        value, = struct.unpack_from('<I', data, address - BASE)
        target = value & ~1
        if BASE <= target < END or 0x20003000 <= target < 0x20030000 or 0xa0000000 <= target < 0xa1000000:
            group = next((name for name, (lo, hi) in SPANS.items() if lo <= address < hi), 'unexpected')
            address_space = ('stage2_iram' if BASE <= target < END else
                             'stage2_dram' if 0x20003000 <= target < 0x20030000 else
                             'mmio')
            rows.append({'word_address': hex(address), 'value': hex(value),
                         'address_space': address_space, 'group': group})
    assert len(rows) == 93
    assert not any(r['group'] == 'unexpected' for r in rows)
    counts = {name: sum(r['group'] == name and r['address_space'] == 'stage2_iram'
                        for r in rows) for name in SPANS}
    assert counts == {'clock_uart_records': 0,
                      'audio_root_callbacks_state': 21,
                      'flash_descriptor_callbacks_profiles': 29,
                      'normal_initialized_tail': 12}
    address_space_counts = {space: sum(r['address_space'] == space for r in rows)
                            for space in ('stage2_iram', 'stage2_dram', 'mmio')}
    assert address_space_counts == {'stage2_iram': 62, 'stage2_dram': 29, 'mmio': 2}
    receipt = {'stock_sha256': hashlib.sha256(data).hexdigest(),
               'scan_range': ['0x100168c0', hex(END)],
               'pointer_filter': 'aligned words whose low-bit-cleared value falls in stage2 IRAM, stage2 DRAM or MMIO ranges',
               'iram_group_counts': counts,
               'address_space_counts': address_space_counts, 'rows': rows,
               'limits': ['Computed, compressed and unaligned addresses are outside this scan.',
                          'A recognized address group is not whole-body or hardware validation.']}
    out = HERE / 'initialized-pointer-roots-receipt.json'
    out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(out)

if __name__ == '__main__':
    main()
