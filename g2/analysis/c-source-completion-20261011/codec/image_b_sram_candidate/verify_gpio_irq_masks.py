#!/usr/bin/env python3
"""Bind native adjacent GPIO IRQ mask loads to a source-owned BSS pair."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_gpio_irq_masks.c'
consumer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_main_initial_leaves.c'
selected = here / 'build-stage2-gpio-irq-masks-round'
final = here / 'build-stock-length-gpio-irq-masks-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x1000482c', '--stop-address=0x10004838', str(stock)], text=True)
for evidence in ('1000482c:', '0x200173a0', '10004830:',
                 'ld.w', '10004834:', '(r2, 0x4)'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '200173a0 00000008 B gx8002_image_b_gpio_irq_masks_200173a0' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_gpio_irq_masks.o')], text=True)
assert '.bss.image_b_gpio_irq_masks 00000008' in sections
assert 'gx8002_image_b_gpio_irq_masks_200173a0[2]' in source.read_text()
assert 'gx8002_image_b_gpio_irq_masks_200173a0[1]' in consumer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_GPIO_IRQ_MASKS_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'consumer_sha256': sha(consumer),
    'native_address': '0x200173a0',
    'native_reads': ['0x10004830 word +0', '0x10004834 word +4'],
    'source_object_bytes': 8, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['A retained-path producer and values are not established.',
               'Physical IRQ-controller effects remain unqualified.']}
(final / 'gpio-irq-masks-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
