#!/usr/bin/env python3
"""Bind the native 144-byte PMU record to source-owned BSS."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_pmu_record.c'
consumer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_pmu_initialize.c'
selected = here / 'build-stage2-pmu-record-round'
final = here / 'build-stock-length-pmu-record-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x1000a74c', '--stop-address=0x1000a77a', str(stock)], text=True)
for evidence in ('1000a750:', '0x2002cb88', '1000a772:', '144',
                 '1000a776:', '1000a778:'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '2002cb88 00000090 B gx8002_image_b_pmu_record_2002cb88' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_pmu_record.o')], text=True)
assert '.bss.image_b_pmu_record 00000090' in sections
assert 'gx8002_image_b_pmu_record_2002cb88[36]' in source.read_text()
assert 'record, 0u, 144u' in consumer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_PMU_RECORD_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'consumer_sha256': sha(consumer),
    'native_address': '0x2002cb88', 'native_cold_clear_bytes': 144,
    'source_object_bytes': 144, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['Warm callback count and contents are not proven.',
               'PMU hardware and resource control effects remain unqualified.']}
(final / 'pmu-record-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
