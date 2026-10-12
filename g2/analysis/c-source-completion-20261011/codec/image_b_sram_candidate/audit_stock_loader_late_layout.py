#!/usr/bin/env python3
"""Compare the experimental late section with the authenticated stock B copy."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGES = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images'
LINK = HERE / 'build-late-audio-source-final-round/receipt.json'
STOCK_LOADER = HERE / 'stock-stage1-loader-receipt.json'


def main():
    stage1 = (IMAGES / 'binh_b_stage1.bin').read_bytes()
    stock = json.loads(STOCK_LOADER.read_text())
    linked = json.loads(LINK.read_text())
    assert hashlib.sha256(stage1).hexdigest() == stock['stage1_sha256']
    start = int(stock['normal_branch']['destination'], 16)
    count = stock['normal_branch']['copy_bytes']
    assert start == 0x10003000 and count == 0x1408c
    assert int.from_bytes(stage1[12:16], 'little') == count
    late = linked['sections']['.late_audio']
    late_start = late['vma']
    late_end = late_start + late['size']
    stock_end = start + count
    assert late_start == 0x1002d800 and late_end == 0x1002e1e8
    assert stock_end == 0x1001708c and stock_end < late_start
    contiguous_length = late_end - start
    native_bss = (0x20017090, 0x2002d79c)
    retained = (0x2002d79c, 0x2002d7b8)
    assumed_alias_payload = (0x20000000 + (stock_end & 0xfffffff),
                             0x20000000 + (late_start & 0xfffffff))
    # The copy address arithmetic is indisputable. DRAM alias interpretation
    # is SDK-supported, not a stock-hardware proof.
    assert assumed_alias_payload[0] == 0x2001708c
    assert assumed_alias_payload[1] == 0x2002d800
    receipt = {
        'result': 'PASS_NEGATIVE_STOCK_LOADER_COVERAGE',
        'stock_stage1_sha256': stock['stage1_sha256'],
        'final_layout_receipt_sha256': hashlib.sha256(LINK.read_bytes()).hexdigest(),
        'stock_normal_copy': [hex(start), hex(stock_end)],
        'stock_copy_bytes': count,
        'late_audio': [hex(late_start), hex(late_end)],
        'late_audio_bytes': late['size'],
        'late_audio_outside_stock_copy': late_start >= stock_end,
        'contiguous_payload_bytes_needed_through_late_end': contiguous_length,
        'additional_bytes_vs_stock_payload': contiguous_length - count,
        'sdk_alias_interpretation_of_added_interval': [hex(x) for x in assumed_alias_payload],
        'sdk_alias_interval_covers_native_bss': assumed_alias_payload[0] < native_bss[1] and native_bss[0] < assumed_alias_payload[1],
        'sdk_alias_interval_covers_retained': assumed_alias_payload[0] < retained[1] and retained[0] < assumed_alias_payload[1],
        'limits': [
            'Stock normal branch copies exactly the original 0x1408c bytes; it never loads late audio.',
            'A contiguous extended copy would cross BSS and retained addresses under the pinned SDK alias model; physical alias behavior remains unverified.',
            'No stock-loader patch, split transfer, updated package, hardware execution or stack maximum is proven.'
        ]
    }
    out = HERE / 'stock-loader-late-layout-receipt.json'
    out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
