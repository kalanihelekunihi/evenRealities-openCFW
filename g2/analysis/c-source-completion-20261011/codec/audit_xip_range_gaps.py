#!/usr/bin/env python3
"""Measure gaps in retained Ghidra function ranges before XIP data-tail."""
import json
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CATALOGUE = ROOT / ('g2/research/corpus/codec/ghidra/open-2026-09-29/'
                    'image_a_xip/functions-000.jsonl')
LOW = 0x10203004
HIGH = 0x1020a8aa
IMAGE = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_xip.bin')
native = IMAGE.read_bytes()
assert len(native) >= HIGH-LOW
# Exceptional gaps have been inspected against native instruction bytes and
# adjacent Ghidra functions. The source names below identify semantic
# candidates; they do not establish exact final relocation or execution.
EXCEPTIONS = {
    0x10203dc2: ('mixed_scalar_literal', '_ain_reset bit mask literal'),
    0x10204b9a: ('branch_case_code', 'gx8002_aout_set_lodac case block'),
    0x10204c3e: ('branch_case_code', 'gx8002_aout_set_lodac case tails'),
    0x10205946: ('mixed_scalar_literal', 'gx8002_snpu_tcb_init mask/address pool'),
    0x10205e1e: ('mixed_scalar_literal', 'gx8002_snpu_run_task mask/address pool'),
    0x10205fe6: ('branch_case_code', 'gx8002_gpio_enable_trigger case block'),
    0x10206012: ('branch_case_code', 'gx8002_gpio_enable_trigger case blocks'),
    0x102061fc: ('mixed_scalar_literal', 'gx8002_dw_spi_setup 10000000 literal'),
    0x10206d7e: ('mixed_scalar_literal', 'gx8002_kws_flash_load f804/address pool'),
    0x10207020: ('return_instruction', 'audio input IRQ jmp r15'),
    0x10207a06: ('mixed_string_literal', 'gx8002_lvp_system_initialize pool'),
    0x1020852a: ('mixed_string_literal', 'UartMessageAsyncInit pool'),
    0x10208b46: ('mixed_scalar_literal', 'gx8002_kws_strategy float/address pool'),
    0x102096a4: ('mixed_string_literal', 'gx8002_app_command_callback pool'),
    0x10209d02: ('division_continuation_code', 'unsigned division continuation'),
    0x10209da2: ('division_continuation_code', 'unsigned division tail'),
}
ranges = []
for line in CATALOGUE.open():
    body = json.loads(line)
    if int(body['entry'], 16) >= HIGH:
        continue
    for first, last in body['ranges']:
        first = max(int(first, 16), LOW)
        last = min(int(last, 16) + 1, HIGH)
        if first < last:
            ranges.append((first, last))
ranges.sort()
merged = []
for first, last in ranges:
    if merged and first <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(last, merged[-1][1]))
    else:
        merged.append((first, last))
gaps = []
cursor = LOW
for first, last in merged:
    if first > cursor:
        gaps.append((cursor, first))
    cursor = max(cursor, last)
if cursor < HIGH:
    gaps.append((cursor, HIGH))
assert sum(last-first for first,last in merged) + sum(
    last-first for first,last in gaps) == HIGH-LOW
receipt = {
    'span': [hex(LOW), hex(HIGH)],
    'span_bytes': HIGH-LOW,
    'catalogue_range_union_bytes': sum(last-first for first,last in merged),
    'gap_count': len(gaps),
    'gap_bytes': sum(last-first for first,last in gaps),
    'native_sha256': hashlib.sha256(native).hexdigest(),
    'largest_gaps': [
        {'start': hex(first), 'end_exclusive': hex(last), 'bytes': last-first}
        for first,last in sorted(gaps, key=lambda pair: pair[0]-pair[1])[:25]
    ],
    'limit': 'Catalogue range gaps mix literal pools, jump case blocks, and missing attribution; not missing-body count',
}
def address_word(word):
    return (0x10000000 <= word < 0x10300000 or
            0x20000000 <= word < 0x21000000 or
            0xa0000000 <= word < 0xb0000000 or
            0xe0000000 <= word < 0xf0000000)

rows = []
for first,last in gaps:
    data = native[first-LOW:last-LOW]
    aligned = data
    alignment = False
    if first % 4 == 2 and data[:2] == b'\0\0':
        aligned = data[2:]
        alignment = True
    words = ([int.from_bytes(aligned[i:i+4], 'little')
              for i in range(0,len(aligned),4)]
             if len(aligned) % 4 == 0 else [])
    if not any(data):
        kind = 'zero_alignment'
    elif len(aligned) % 4:
        kind = 'mixed_nonword_requires_native_review'
    elif all(map(address_word, words)):
        kind = 'address_literal_words'
    elif any(map(address_word, words)):
        kind = 'mixed_address_constant_or_code_requires_native_review'
    else:
        kind = 'constant_or_code_requires_native_review'
    note = None
    if first in EXCEPTIONS:
        kind,note = EXCEPTIONS[first]
    rows.append({'start':hex(first),'end_exclusive':hex(last),
                 'bytes':last-first,'sha256':hashlib.sha256(data).hexdigest(),
                 'kind':kind,'two_byte_alignment':alignment,
                 'attribution':note,
                 'words':[hex(w) for w in words] if len(words)<=32 else [],
                 'raw_hex':data.hex() if len(data)<=16 else None})
receipt['gaps'] = rows
receipt['classification_counts'] = {kind:sum(row['kind']==kind for row in rows)
                                    for kind in sorted({row['kind'] for row in rows})}
receipt['classification_bytes'] = {kind:sum(row['bytes'] for row in rows
                                            if row['kind']==kind)
                                     for kind in receipt['classification_counts']}
assert len(EXCEPTIONS) == 16
assert not any('requires_native_review' in row['kind'] for row in rows)
(HERE / 'xip-function-range-gap-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in
                  ('span_bytes','catalogue_range_union_bytes','gap_count','gap_bytes')}))
