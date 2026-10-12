#!/usr/bin/env python3
"""Check SDK-correlated 96-byte SPI state and native subrecord placement."""
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
tools = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
sdk = root / 'third-party/upstream/nationalchip-lvp-kws/drivers_lib/spi/dw_spi/spi_master_v3.o'
source = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_spi_device_state.c'
producer = root / 'g2/components/gx8002/image_b_sram_candidate/backup_stage2_board_devices_initialize.c'
selected = here / 'build-stage2-spi-sdk-record-round'
final = here / 'build-stock-length-spi-sdk-record-round'
elf = final / 'image_b_flexible_source_probe.elf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

sdk_symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(sdk)], text=True)
for evidence in ('00000000 00000010 b spi_device_context_tab',
                 '00000010 00000024 b dw_spi_master',
                 '00000034 0000002c b dwspi'):
    assert evidence in sdk_symbols, evidence
dis = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-D', '-b',
    'binary', '-m', 'csky', '--adjust-vma=0x10003000',
    '--start-address=0x100085ac', '--stop-address=0x100085d8', str(stock)], text=True)
for evidence in ('100085ae:', '0x20017670', '100085b0:', '52',
                 '100085b8:', '16', '100085c2:', '(r2, 0x34)',
                 '100085c4:', '(r2, 0x28)'):
    assert evidence in dis, evidence
symbols = subprocess.check_output([str(tools / 'csky-elfabiv2-nm'), '-S', str(elf)], text=True)
assert '20017670 00000060 B gx8002_image_b_spi_device_state_20017670' in symbols
sections = subprocess.check_output([str(tools / 'csky-elfabiv2-objdump'), '-h',
    str(selected / 'backup_stage2_spi_device_state.o')], text=True)
assert '.bss.image_b_spi_device_state 00000060' in sections
assert 'gx8002_image_b_spi_device_state_20017670[24]' in source.read_text()
assert 'base + 13u' in producer.read_text()
assert 'base + 4u' in producer.read_text()
payload = final / 'image_b_source_payload.bin'
assert payload.stat().st_size == 82060
receipt = {
    'status': 'PASS_SDK_CORRELATED_SPI_STATE_SOURCE_PLACEMENT',
    'native_stage2_sha256': sha(stock), 'pinned_sdk_object_sha256': sha(sdk),
    'selected_elf_sha256': sha(elf), 'source_sha256': sha(source),
    'producer_sha256': sha(producer), 'native_address': '0x20017670',
    'sdk_local_bss_bytes': {'spi_device_context_tab':16,'dw_spi_master':36,'dwspi':44},
    'native_subrecord_offsets': ['0x10 master','0x34 dwspi'],
    'source_object_bytes': 96, 'source_storage': 'NOBITS/NOLOAD',
    'stock_transfer_payload_bytes': payload.stat().st_size,
    'limits': ['The pinned SDK object corroborates record shape but is not byte-identical to the product binary.',
               'Warm state and physical SPI controller effects remain unqualified.']}
(final / 'spi-sdk-record-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
