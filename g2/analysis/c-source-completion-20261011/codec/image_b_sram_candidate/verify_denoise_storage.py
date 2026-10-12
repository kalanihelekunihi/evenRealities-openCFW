#!/usr/bin/env python3
"""Check disjoint denoise prefix, queue and buffer source BSS objects."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
sdk = root / 'third-party/upstream/nationalchip-lvp-kws/lvp/common/lvp_queue.h'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_denoise_runtime_storage.c'
initializer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_denoise_mode_init_experiment.c'
selected = here / 'build-stage2-denoise-storage-round'
final = here / 'build-stock-length-denoise-storage-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x1000bc6a', '--stop-address=0x1000bc82', str(stock)], text=True)
for evidence in ('1000bc6a:', '0x2002d2bc', '1000bc72:', '4',
                 '1000bc74:', '40', '1000bc76:', '52',
                 '1000bc7a:', '28', '1000bc7e:', '0x10009fa8'):
    assert evidence in dis, evidence
queue_init = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10009fa8', '--stop-address=0x10009fbc', str(stock)], text=True)
for evidence in ('(r0, 0x0)', '(r0, 0x4)', '(r0, 0x8)',
                 '(r0, 0xc)', '(r0, 0x10)'):
    assert evidence in queue_init, evidence
sdk_text = sdk.read_text()
for evidence in ('int tail;', 'int head;', 'unsigned char *buffer;',
                 'int size;', 'int member_size;'):
    assert evidence in sdk_text, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
objects = (
    ('2002d2bc','0000001c','gx8002_image_b_denoise_mode_state_2002d2bc'),
    ('2002d2d8','00000014','gx8002_image_b_denoise_ring_2002d2d8'),
    ('2002d2f0','00000028','gx8002_image_b_denoise_queue_buffer_2002d2f0'),
)
for address, size, name in objects:
    assert f'{address} {size} B {name}' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_denoise_runtime_storage.o')], text=True)
for evidence in ('.bss.image_b_denoise_mode_prefix 0000001c',
                 '.bss.image_b_denoise_queue 00000014',
                 '.bss.image_b_denoise_queue_buffer 00000028'):
    assert evidence in sections, evidence
assert 'gx8002_image_b_denoise_mode_state_2002d2bc[28]' in source.read_text()
assert 'gx8002_image_b_denoise_ring_2002d2d8[5]' in source.read_text()
assert 'gx8002_image_b_denoise_queue_buffer_2002d2f0[40]' in source.read_text()
assert 'gx8002_image_b_denoise_queue_buffer_2002d2f0,' in initializer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_DENOISE_STORAGE_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'sdk_queue_header_sha256': sha(sdk),
    'selected_elf_sha256': sha(elf), 'source_sha256': sha(source),
    'initializer_sha256': sha(initializer),
    'objects': [{'address':'0x2002d2bc','bytes':28,'role':'mode prefix'},
                {'address':'0x2002d2d8','bytes':20,'role':'five-word queue'},
                {'address':'0x2002d2f0','bytes':40,'role':'queue buffer'}],
    'unattributed_gap': '0x2002d2ec..0x2002d2f0 (4 bytes)',
    'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['The four-byte gap remains unattributed.',
               'Queue lifecycle, product denoise selection and physical audio behavior remain unqualified.']}
(final / 'denoise-storage-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
