#!/usr/bin/env python3
"""Bind native stage2 console port word to its source-owned BSS object."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_console_port.c'
writer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_main_initial_leaves.c'
reader = root / 'g2/components/gx8002/image_b_sram_candidate/backup_uart_debug_putchar.c'
selected = here / 'build-stage2-console-port-round'
final = here / 'build-stock-length-console-port-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x10004808', '--stop-address=0x10004824', str(stock)], text=True)
for evidence in ('1000480a:', '0x2001739c', '1000480c:', 'st.w',
                 '1000481a:', '1000481e:', 'ld.w'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '2001739c 00000004 B gx8002_image_b_console_port_2001739c' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_console_port.o')], text=True)
assert '.bss.image_b_console_port 00000004' in sections
assert 'volatile uint32_t gx8002_image_b_console_port_2001739c' in source.read_text()
assert 'gx8002_image_b_console_port_2001739c = port' in writer.read_text()
assert 'port = gx8002_image_b_console_port_2001739c' in reader.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_BOUNDED_CONSOLE_PORT_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'selected_elf_sha256': sha(elf),
    'source_sha256': sha(source), 'writer_sha256': sha(writer),
    'reader_sha256': sha(reader), 'native_address': '0x2001739c',
    'native_write': '0x1000480c word', 'native_read': '0x1000481e word',
    'source_object_bytes': 4, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['The word is cleared only on the native non-retained reset path.',
               'UART device effects and retained runtime value remain unqualified.']}
(final / 'console-port-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
