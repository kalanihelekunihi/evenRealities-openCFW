#!/usr/bin/env python3
"""Check the source-owned ten-record native timer BSS interval."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_timer_records.c'
consumer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_timer_initialize.c'
selected = here / 'build-stage2-timer-records-round'
final = here / 'build-stock-length-timer-records-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10005038', '--stop-address=0x10005042', str(stock)], text=True)
for evidence in ('10005038:', '360', '1000503e:', '0x200174bc'):
    assert evidence in dis, evidence
loop = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x100050cc', '--stop-address=0x100050dc', str(stock)], text=True)
for evidence in ('100050ce:', '0x200174bc', '100050d0:', '360', '100050da:', '36'):
    assert evidence in loop, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '200174bc 00000168 B gx8002_image_b_timer_records_200174bc' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_timer_records.o')], text=True)
assert '.bss.image_b_timer_records 00000168' in sections
assert 'gx8002_image_b_timer_records_200174bc[90]' in source.read_text()
assert 'gx8002_image_b_timer_records_200174bc + index * 9u' in consumer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_TIMER_RECORDS_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'consumer_sha256': sha(consumer),
    'native_address': '0x200174bc', 'native_clear_bytes': 360,
    'native_record_count': 10, 'native_record_stride_bytes': 36,
    'source_object_bytes': 360, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['Timer callbacks, scheduler time and physical timer effects remain unqualified.',
               'The timer initializer clears the records; retained contents before that initializer may differ.']}
(final / 'timer-records-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
