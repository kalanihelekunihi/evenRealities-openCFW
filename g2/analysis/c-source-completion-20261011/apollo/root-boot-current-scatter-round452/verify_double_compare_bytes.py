#!/usr/bin/env python3
"""Check both selected binary64 flag helpers against the authenticated Boot span."""
import hashlib
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/runtime_memory/double_compare_flags.S'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / 'compare.o'
    binary = Path(directory) / 'compare.bin'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55',
                    '-mthumb', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(obj),
                    str(binary)], check=True)
    candidate = binary.read_bytes()
assert len(candidate) == 104
for index, address in enumerate((0x422698, 0x4226cc)):
    assert candidate[index*52:(index+1)*52] == blob[address-0x410000:address-0x410000+52]
print('PASS_DOUBLE_COMPARE_FLAGS_STOCK_BYTES 2 104')
