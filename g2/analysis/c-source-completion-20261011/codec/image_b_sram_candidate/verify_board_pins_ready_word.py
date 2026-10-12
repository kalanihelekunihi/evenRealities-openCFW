#!/usr/bin/env python3
"""Bind native pin-ready word accesses to a source-owned NOLOAD object."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_board_pins_ready.c'
reader = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_board_pins_finish.c'
writer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_board_pins_initialize.c'
selected = here / 'build-stage2-board-pins-ready-round'
final = here / 'build-stock-length-board-pins-ready-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x1000888c', '--stop-address=0x100089d6', str(stock)], text=True)
for evidence in ('1000888e:', 'lrw', '0x200176d8', '10008892:',
                 'ld.w', '100089d0:', '100089d2:', 'movi',
                 '100089d4:', 'st.w'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '200176d8 00000004 B gx8002_image_b_board_pins_ready_200176d8' in symbols
object_path = selected / 'backup_stage2_board_pins_ready.o'
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h', str(object_path)], text=True)
assert '.bss.image_b_board_pins_ready 00000004' in sections
assert 'volatile uint32_t gx8002_image_b_board_pins_ready_200176d8' in source.read_text()
assert 'gx8002_image_b_board_pins_ready_200176d8 == 0u' in reader.read_text()
assert 'gx8002_image_b_board_pins_ready_200176d8 = 1u' in writer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_BOARD_PINS_READY_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'reader_sha256': sha(reader),
    'writer_sha256': sha(writer), 'native_address': '0x200176d8',
    'native_read': '0x10008892 word',
    'native_write': '0x100089d4 word value 1',
    'source_object_bytes': 4, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['The word is cold-cleared only on the native non-retained reset path.',
               'Pin MMIO effects and retained runtime value remain unqualified.']}
(final / 'board-pins-ready-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
