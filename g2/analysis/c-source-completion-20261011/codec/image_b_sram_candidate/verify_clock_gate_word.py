#!/usr/bin/env python3
"""Bind the native clock-gate read to source BSS without assuming its value."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_clock_gate_bits.c'
consumer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_clock_init_experiment.c'
selected = here / 'build-stage2-clock-gate-word-round'
final = here / 'build-stock-length-clock-gate-word-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10003400', '--stop-address=0x1000340c', str(stock)], text=True)
for evidence in ('10003402:', '0x20017394', '10003404:', 'ld.w'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '20017394 00000004 B gx8002_image_b_clock_gate_bits_20017394' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_clock_gate_bits.o')], text=True)
assert '.bss.image_b_clock_gate_bits 00000004' in sections
assert 'volatile uint32_t gx8002_image_b_clock_gate_bits_20017394' in source.read_text()
assert 'gx8002_image_b_clock_gate_bits_20017394 >> module' in consumer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_CLOCK_GATE_WORD_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'consumer_sha256': sha(consumer),
    'native_address': '0x20017394', 'native_read': '0x10003404 word',
    'source_object_bytes': 4, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['A retained-path producer and value are not established.',
               'Clock gate hardware effects remain unqualified.']}
(final / 'clock-gate-word-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
