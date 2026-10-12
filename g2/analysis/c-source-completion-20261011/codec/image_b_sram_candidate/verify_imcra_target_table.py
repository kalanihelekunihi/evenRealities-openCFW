#!/usr/bin/env python3
"""Compare compiled full or quarter-wave sine source with authenticated ROM."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / 'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
parser = argparse.ArgumentParser()
parser.add_argument('--object', type=Path,
                    default=HERE / 'build-imcra-final-round/backup_imcra_cosine_lookup.o')
args = parser.parse_args()
candidate = args.object.resolve()
assert candidate.is_file()
stock = IMAGE.read_bytes()
assert hashlib.sha256(stock).hexdigest() == \
    'd23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941'
command = ['docker', 'run', '--rm', '--network=none', '--read-only',
           '--platform', 'linux/amd64',
           '--mount', f'type=bind,src={TOOL},dst=/tool,readonly',
           '--mount', f'type=bind,src={candidate.parent},dst=/out,readonly',
           'opencfw/iar-base:10.10.2-local',
           '/tool/bin/csky-abiv2-elf-objdump', '-s', '-j', '.rodata',
           '/out/' + candidate.name]
output = subprocess.run(command, check=True, capture_output=True, text=True).stdout
compiled = bytearray()
for line in output.splitlines():
    match = re.match(r'^\s*[0-9a-f]{4,8}\s+((?:[0-9a-f]{8}\s*){1,4})', line)
    if match:
        compiled.extend(bytes.fromhex(match.group(1)))
expected = stock[0x100148d4 - 0x10003000:
                 0x100148d4 - 0x10003000 + 513 * 4]
assert len(expected) == 2052
if len(compiled) == len(expected):
    assert bytes(compiled) == expected
    representation = 'full-native-table'
elif len(compiled) == 129 * 4:
    quarter = list(struct.unpack('<129I', compiled))
    words = []
    for index in range(513):
        if index <= 128:
            word = quarter[index]
        elif index < 256:
            word = quarter[256 - index]
        elif index == 256:
            word = 0x2768d16e
        elif index <= 384:
            word = quarter[index - 256] ^ 0x80000000
        elif index < 512:
            word = quarter[512 - index] ^ 0x80000000
        else:
            word = 0xa7e8d16e
        words.append(word)
    assert struct.pack('<513I', *words) == expected
    representation = 'quarter-wave-with-two-native-residuals'
else:
    raise AssertionError(f'unexpected compiled sine data length {len(compiled)}')
print(json.dumps({'object_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
                  'native_table_address': '0x100148d4',
                  'reconstructed_float32_words': 513,
                  'compiled_data_bytes': len(compiled),
                  'representation': representation,
                  'result': 'PASS',
                  'limit': 'Compiled data reconstructs stock table; floating instruction effects and hardware timing remain unqualified.'}))
