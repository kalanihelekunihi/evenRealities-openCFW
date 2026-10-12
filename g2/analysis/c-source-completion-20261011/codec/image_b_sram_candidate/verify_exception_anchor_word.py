#!/usr/bin/env python3
"""Check the source-owned native exception stack anchor, not its frame."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_exception_anchor.c'
consumer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_exception_experiment.c'
selected = here / 'build-stage2-exception-anchor-round'
final = here / 'build-stock-length-exception-anchor-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10003208', '--stop-address=0x10003220', str(stock)], text=True)
for evidence in ('10003208:', '0x20017390', '1000320c:', 'st.w',
                 '10003210:', '1000321c:', 'ld.w', 'subi', '72'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '20017390 00000004 B gx8002_image_b_exception_scratch_20017390' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_exception_anchor.o')], text=True)
assert '.bss.image_b_exception_anchor 00000004' in sections
assert 'gx8002_image_b_exception_scratch_20017390[1]' in source.read_text()
assert 'lrw r13, gx8002_image_b_exception_scratch_20017390' in consumer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_EXCEPTION_ANCHOR_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'consumer_sha256': sha(consumer),
    'native_address': '0x20017390', 'native_word_store': '0x1000320c',
    'native_word_load': '0x1000321c', 'source_object_bytes': 4,
    'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['Only the anchor word is source-owned. The native exception frame spans 72 bytes below this address and is a separate runtime storage contract.',
               'Exception-path execution and diagnostic consumer effects remain unqualified.']}
(final / 'exception-anchor-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
