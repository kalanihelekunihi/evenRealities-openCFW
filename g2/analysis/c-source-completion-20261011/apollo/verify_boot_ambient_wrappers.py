#!/usr/bin/env python3
"""Compare source Thumb wrappers with locked stock, excluding relocated BL."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
cases = [
    ('filesystem/native_unmount_abi_wrapper.S', 0x414948, 8, 2),
    ('initializer_callbacks/native_uart_log_abi_wrapper.S', 0x41b854, 14, 8),
]
for rel, address, length, branch_offset in cases:
    source = ROOT / 'g2/components/bootloader' / rel
    with tempfile.TemporaryDirectory() as temp:
        obj = Path(temp) / 'wrapper.o'
        raw = Path(temp) / 'wrapper.bin'
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                        '-mfpu=fpv5-sp-d16','-mfloat-abi=softfp','-c',str(source),'-o',str(obj)],check=True)
        subprocess.run(['/opt/homebrew/bin/arm-none-eabi-objcopy','-O','binary',str(obj),str(raw)],check=True)
        candidate = raw.read_bytes()
    native = blob[address - 0x410000:address - 0x410000 + length]
    assert len(candidate) == length, (rel,len(candidate),length)
    assert candidate[:branch_offset] == native[:branch_offset], (rel,'before branch')
    assert candidate[branch_offset+4:] == native[branch_offset+4:], (rel,'after branch')
    print(f'PASS {rel} {length-4}/{length} fixed bytes; BL relocation retained')
