#!/usr/bin/env python3
"""Measure stock image-A SRAM bytes outside retained Ghidra function ranges.

This is a byte-partition audit, not an assertion that the uncovered bytes are
all data or that covered function ranges are source-equivalent.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 0x10023400
CAT = ROOT / ('g2/research/corpus/codec/ghidra/open-2026-09-29/'
              'image_a_sram/functions-000.jsonl')
IMAGE = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_sram.bin')
raw = IMAGE.read_bytes()
HIGH = BASE + len(raw)
ranges = []
functions = []
for line in CAT.open():
    body = json.loads(line)
    functions.append((int(body['entry'],16), body['name']))
    for first,last in body['ranges']:
        first = max(BASE,int(first,16))
        last = min(HIGH,int(last,16)+1)
        if first < last:
            ranges.append((first,last))
ranges.sort()
merged = []
for first,last in ranges:
    if merged and first <= merged[-1][1]:
        merged[-1] = (merged[-1][0],max(merged[-1][1],last))
    else:
        merged.append((first,last))
gaps = []
cursor = BASE
for first,last in merged:
    if cursor < first:
        gaps.append((cursor,first))
    cursor = max(cursor,last)
if cursor < HIGH:
    gaps.append((cursor,HIGH))
assert sum(b-a for a,b in merged)+sum(b-a for a,b in gaps)==len(raw)
rows = []
for first,last in gaps:
    segment = raw[first-BASE:last-BASE]
    before = max((p for p in functions if p[0] < first),default=None)
    after = min((p for p in functions if p[0] >= last),default=None)
    rows.append({'start':hex(first),'end_exclusive':hex(last),
                 'bytes':last-first,
                 'sha256':hashlib.sha256(segment).hexdigest(),
                 'prefix_hex':segment[:48].hex(),
                 'zero_bytes':segment.count(0),
                 'preceding_function':before,
                 'following_function':after})
receipt = {'image_sha256':hashlib.sha256(raw).hexdigest(),
           'base':hex(BASE),'end_exclusive':hex(HIGH),
           'image_bytes':len(raw),
           'function_range_union_bytes':sum(b-a for a,b in merged),
           'gap_count':len(gaps),'gap_bytes':sum(b-a for a,b in gaps),
           'gaps':rows,
           'limit':'Gaps contain vectors, initialized data, literal pools, branch case blocks, and unseeded code; no complete-source claim.'}
# These are source-owned semantic data extents. Only the vector and prior
# product-data receipts establish section placement to date; current board,
# flash, and sample objects have target scalar/relocation checks. Subtracting
# their stock extents identifies the still-unpartitioned function-range gaps.
source_data = [
    (0x10023400,0x10023500,'vector table'),
    (0x100264e4,0x1002657c,'flash state and API relocations'),
    (0x1002657c,0x100269cc,'OTP, module, clock, board prefix data'),
    (0x100269cc,0x10026a94,'board configuration extension'),
    (0x10026a94,0x10026b94,'UART channel records'),
    (0x10026b94,0x10026c74,'AOUT context/table/config'),
    (0x10026c74,0x10026d7c,'KWS/sample/request tail'),
]
assert source_data[0][1]-source_data[0][0] == 256
assert source_data[1][0] == 0x100264e4
assert source_data[-1][1] == HIGH
assert all(source_data[i][1] == source_data[i+1][0]
           for i in range(1,len(source_data)-1))
assert sum(last-first for first,last,_ in source_data[1:]) == 2200
residual = []
for first,last in gaps:
    pieces = [(first,last)]
    for data_first,data_last,_ in source_data:
        next_pieces = []
        for piece_first,piece_last in pieces:
            if piece_last <= data_first or piece_first >= data_last:
                next_pieces.append((piece_first,piece_last))
            else:
                if piece_first < data_first:
                    next_pieces.append((piece_first,data_first))
                if piece_last > data_last:
                    next_pieces.append((data_last,piece_last))
        pieces = next_pieces
    residual.extend(pieces)
receipt['source_data_intervals'] = [
    {'start':hex(first),'end_exclusive':hex(last),'kind':name}
    for first,last,name in source_data]
receipt['source_data_overlap_gap_bytes'] = receipt['gap_bytes']-sum(
    last-first for first,last in residual)
receipt['residual_gap_count'] = len(residual)
receipt['residual_gap_bytes'] = sum(last-first for first,last in residual)
receipt['residual_gaps'] = [
    {'start':hex(first),'end_exclusive':hex(last),'bytes':last-first,
     'sha256':hashlib.sha256(raw[first-BASE:last-BASE]).hexdigest(),
     'prefix_hex':raw[first-BASE:last-BASE][:48].hex()}
    for first,last in residual]
def address_word(word):
    return (0x10000000 <= word < 0x10300000 or
            0x20000000 <= word < 0x21000000 or
            0xa0000000 <= word < 0xb0000000 or
            0xe0000000 <= word < 0xf0000000)

for row,(first,last) in zip(receipt['residual_gaps'],residual):
    data = raw[first-BASE:last-BASE]
    aligned = data[2:] if first%4==2 and data[:2]==b'\0\0' else data
    if not any(data):
        kind='zero_alignment'
    elif len(aligned)%4:
        kind='nonword_native_review'
    else:
        words=[int.from_bytes(aligned[i:i+4],'little')
               for i in range(0,len(aligned),4)]
        if all(map(address_word,words)):
            kind='address_literal_words'
        elif any(map(address_word,words)):
            kind='mixed_native_review'
        else:
            kind='scalar_or_code_native_review'
    row['structural_class']=kind
receipt['residual_structural_counts']={
    kind:sum(row['structural_class']==kind for row in receipt['residual_gaps'])
    for kind in sorted({row['structural_class'] for row in receipt['residual_gaps']})}
receipt['residual_structural_bytes']={
    kind:sum(row['bytes'] for row in receipt['residual_gaps']
             if row['structural_class']==kind)
    for kind in receipt['residual_structural_counts']}
large_review = {
    0x100253b8: ('constant_and_jump_table', 'platform/clock native address table; final relocations open'),
    0x100260e4: ('already_sourced_unseeded_code', 'resident_tws_buffer_update.c'),
    0x10024846: ('adjacent_case_block_candidate', 'resident_platform_read.c'),
    0x10025dc2: ('adjacent_case_block_candidate', 'resident_platform_config.c'),
    0x100249a2: ('adjacent_case_block_candidate', 'resident_start_mode.c'),
    0x10024596: ('adjacent_case_block_candidate', 'resident_flash_interface.c'),
    0x10025d80: ('adjacent_case_block_candidate', 'resident_platform_config.c'),
    0x1002351e: ('startup_literal_pool', 'resident_reset_entry_candidate.S'),
    0x1002353e: ('return_and_bss_bound_literals', 'resident_clear_bss.c'),
    0x100235e2: ('startup_register_literals', 'resident_system_initialize_candidate.c'),
    0x10023864: ('flash_getinfo_literal_pool', 'resident_flash_transfer.c'),
    0x1002386e: ('flash_getinfo_case_code', 'resident_flash_transfer.c'),
    0x1002389a: ('flash_getinfo_tail_and_state_literal', 'resident_flash_transfer.c'),
    0x10023d4e: ('flash_read_literal_pool', 'resident_flash_transfer.c'),
    0x10024238: ('flash_discover_literals_and_tail', 'resident_flash_discover.c'),
    0x100246a6: ('flash_initialize_tail_and_literals', 'resident_flash_initialize.c'),
    0x100247ac: ('flash_probe_literals_and_tail', 'resident_flash_probe.c'),
    0x1002481c: ('platform_read_case_code', 'resident_platform_read.c'),
    0x10025122: ('platform_gate_case_code', 'resident_platform_gate.c'),
    0x1002513c: ('platform_gate_case_code', 'resident_platform_gate.c'),
    0x10025148: ('platform_gate_case_code', 'resident_platform_gate.c'),
    0x10025224: ('clock_frequency_literals_and_tail', 'resident_clock_frequency.c'),
    0x10025342: ('clock_frequency_case_code', 'resident_clock_frequency.c'),
    0x10025cec: ('clock_initializer_scalar_literals', 'resident_clock_initialize_candidate.c'),
    0x10025db6: ('platform_config_tail_code', 'resident_platform_config.c'),
}
for row in receipt['residual_gaps']:
    attribution = large_review.get(int(row['start'],16))
    if attribution:
        row['native_attribution_candidate'] = {
            'kind':attribution[0], 'source':attribution[1]}
receipt['large_residual_attribution_count'] = sum(
    'native_attribution_candidate' in row for row in receipt['residual_gaps'])
receipt['large_residual_attribution_bytes'] = sum(
    row['bytes'] for row in receipt['residual_gaps']
    if 'native_attribution_candidate' in row)
assert len(large_review)==25
assert receipt['large_residual_attribution_count']==25
(HERE/'sram-function-range-gap-receipt.json').write_text(
    json.dumps(receipt,indent=2)+'\n')
print(json.dumps({key:receipt[key] for key in
                  ('image_bytes','function_range_union_bytes','gap_count','gap_bytes')}))
