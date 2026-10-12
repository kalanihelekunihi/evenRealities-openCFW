#!/usr/bin/env python3
"""Bind the native 32-entry IRQ registration table to source storage."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_irq_descriptors.c'
registrar = root / 'g2/components/gx8002/image_b_sram_candidate/backup_runtime_helpers.c'
dispatcher = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_generic_irq.c'
selected = here / 'build-stage2-irq-descriptors-round'
final = here / 'build-stock-length-irq-descriptors-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10004844', '--stop-address=0x10004858', str(stock)], text=True)
for evidence in ('10004844:', 'cmphsi', '32', '1000484c:',
                 '0x200173a8', '1000484e:', 'r0 << 3', '10004856:', 'st.w'):
    assert evidence in dis, evidence
dispatch = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x1000489c', '--stop-address=0x100048b0', str(stock)], text=True)
for evidence in ('1000489e:', '0x200173a8', '100048a0:',
                 'r0 << 3', '100048ac:', 'ld.w'):
    assert evidence in dispatch, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '200173a8 00000100 B gx8002_image_b_irq_descriptors_200173a8' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_irq_descriptors.o')], text=True)
assert '.bss.image_b_irq_descriptors 00000100' in sections
assert 'gx8002_image_b_irq_descriptors_200173a8[64]' in source.read_text()
assert 'line >= 32u' in registrar.read_text()
assert 'gx8002_image_b_irq_descriptors_200173a8 + line * 8u' in dispatcher.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_IRQ_DESCRIPTORS_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'registrar_sha256': sha(registrar),
    'dispatcher_sha256': sha(dispatcher), 'native_address': '0x200173a8',
    'registered_lines': 32, 'bytes_per_descriptor': 8,
    'source_object_bytes': 256, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['The hardware-supplied dispatch line is not bounded in the native entry.',
               'Registered lines, retained handlers and physical IRQ delivery remain unqualified.']}
(final / 'irq-descriptors-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
