# SPDX-License-Identifier: MIT
"""Authenticate SPI context extent and census literal pointers; no code extraction."""
import json
import struct
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, IMAGE, IMAGE_SHA, sha, authenticated_blob
from build_transparent_image import Elf32

BLOB = '600d763a219007e2af7b5006989d44984abf0861'
REL = 'drivers_lib/spi/dw_spi/spi_master_v3.o'

def analyze():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    actual = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + REL], text=True).strip()
    assert actual == BLOB
    obj = Elf32(authenticated_blob(sdk / REL, BLOB), 'upstream SPI oracle')
    expected = [('spi_device_context_tab', 0, 16), ('dw_spi_master', 16, 36), ('dwspi', 52, 44)]
    rows = []
    for name, offset, size in expected:
        matches = [s for s in obj.symbols() if s['name'] == name]
        assert len(matches) == 1, (name, matches)
        symbol = matches[0]
        section = obj.sections[symbol['section']]
        assert (symbol['value'], symbol['size'], symbol['type']) == (offset, size, 1)
        assert section['name'] == '.bss' and section['type'] == 8
        rows.append({'symbol': name, 'bss_offset': offset, 'bytes': size})
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    # Search every byte position, not only aligned literal pools. These are
    # raw occurrences, not automatically executed loads or live references.
    pointers = []
    for target in range(0x200176a4, 0x200176d0):
        needle = struct.pack('<I', target)
        offset = stock.find(needle, 0x3b940, 0x4f9cc)
        while offset != -1:
            pointers.append({'target': target, 'context_offset': target - 0x200176a4,
                             'package_offset': offset, 'runtime_address': offset - 0x38940 + 0x10000000})
            offset = stock.find(needle, offset + 1, 0x4f9cc)
    result = {'sdk_commit': SDK_COMMIT, 'oracle_blob': BLOB, 'stock_sha256': IMAGE_SHA,
              'upstream_bss_objects': rows, 'backup_context_address': 0x200176a4,
              'backup_context_extent': 44, 'backup_literal_pointer_occurrences': pointers,
              'has_debug_info': any(s['name'] == '.debug_info' for s in obj.sections),
              'source_admitted': False,
              'limits': ['The upstream object matches primary transfer code; its layout corroborates, but does not prove, the complete backup type.',
                         'Literal occurrences do not cover pointers derived arithmetically or passed indirectly.',
                         'Offset +36 remains semantically unresolved. No claim that it is unused.',
                         'Oracle bytes are never linked into firmware.']}
    (ROOT / 'docs/research/gx8002-backup-spi-context-layout.json').write_text(json.dumps(result, indent=2) + '\n')
    return result

if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))
