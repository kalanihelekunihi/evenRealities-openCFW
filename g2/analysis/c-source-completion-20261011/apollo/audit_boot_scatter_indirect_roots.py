#!/usr/bin/env python3
"""Enumerate aligned flash Thumb pointers in decoded Boot startup SRAM data."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct

root = Path(__file__).resolve().parents[4]
base_path = root / 'g2/components/bootloader/startup/verify.py'
spec = importlib.util.spec_from_file_location('boot_startup_verify', base_path)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
v = base.v
v.ENTRIES['expand_adapter'] = 0x415326
stock = base.Machine()
stock.cpu.mem_write(0x20000000, bytes([0xa5]) * 1371)
stock.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
assert stock.run('expand_adapter', [0x433104])['return'] == 0x433110
decoded = bytes(stock.cpu.mem_read(0x20000000, 1371))
expected_offsets = set(range(0x158, 0x1c4, 4)) | {0x200, 0x204, 0x208,
                                                     0x4cc, 0x4d0, 0x4f4, 0x4f8}
assert len(expected_offsets) == 34
found = {off: struct.unpack_from('<I', decoded, off)[0]
         for off in range(0, len(decoded) - 3, 4)
         if (value := struct.unpack_from('<I', decoded, off)[0]) & 1
         and 0x410001 <= value <= 0x434477}
assert set(found) == expected_offsets, (sorted(set(found)-expected_offsets),
                                        sorted(expected_offsets-set(found)))
result = {
    'status': 'PASS_BOUNDED_SCATTER_ROOT_SCAN',
    'locked_stock_sha256': hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),
    'decoded_sha256': hashlib.sha256(decoded).hexdigest(),
    'decoded_bytes': len(decoded),
    'aligned_thumb_flash_pointer_count': len(found),
    'pointer_offsets_and_values': {hex(off): hex(value) for off, value in found.items()},
    'unbound_offsets': [],
    'limits': [
        'This scan covers only 4-byte aligned Thumb pointers in the 1371-byte startup SRAM record.',
        'Runtime-written tables, unaligned/computed pointers, other initialized objects, ROM callbacks and physical semantics remain outside scope.',
    ],
}
output = Path(__file__).with_name('boot-scatter-indirect-roots.json')
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'],
                  'aligned_thumb_flash_pointer_count': len(found),
                  'unbound_offsets': []}))
