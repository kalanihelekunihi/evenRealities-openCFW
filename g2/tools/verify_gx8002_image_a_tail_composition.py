# SPDX-License-Identifier: MIT
"""Check generated trailer ownership and checksum propagation in composition."""
import json
from pathlib import Path
from build_gx8002_source_candidate import compose
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from generate_gx8002_image_a_tail import BLOCK, PAD, CRC, XIP


def crc_reference(data):
    value = 0xffffffff
    for byte in data:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def verify():
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    cases = 0
    for offset in (None, BLOCK+0x180, BLOCK+0x181, PAD-1):
        replacements = []
        if offset is not None:
            payload = bytes([stock[offset] ^ 0x80])
            # Synthetic mutation tests composition only, not source admission.
            replacements = [{'package_offset':offset,'bytes':1,'payload':payload,
                             'compiled_bytes':1,'compiled_sha256':sha(payload),
                             'sha256':sha(stock[offset:offset+1]),
                             'symbol':'test_only_mutation','ownership_kind':'compiled_c'}]
        output, ownership, totals = compose(stock,replacements)
        assert output[PAD:CRC] == bytes(CRC-PAD)
        assert int.from_bytes(output[CRC:CRC+4],'little') == crc_reference(output[BLOCK+24:CRC])
        assert int.from_bytes(output[CRC+4:XIP],'little') == 0x8e84
        if offset is None: assert output == stock
        else: assert output[CRC:CRC+4] != stock[CRC:CRC+4]
        cursor = 0
        for row in ownership:
            assert row['offset'] == cursor
            cursor += row['size']
            if row['kind'] == 'retained_stock':
                assert cursor <= PAD or row['offset'] >= XIP
        assert cursor == len(stock) == sum(totals.values())
        assert totals['generated_source_data'] == 4092
        assert totals['generated_container_metadata'] == 88
        cases += 1
    return {'composition_cases':cases,'generator_sha256':sha((ROOT/'tools/generate_gx8002_image_a_tail.py').read_bytes()),
            'composer_sha256':sha((ROOT/'tools/build_gx8002_source_candidate.py').read_bytes()),
            'verifier_sha256':sha(Path(__file__).read_bytes()),'source_only':False,
            'limits':['Synthetic mutations test container bookkeeping only; not executable behavior or hardware.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-image-a-tail-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['composition_cases'],'composition cases passed')
