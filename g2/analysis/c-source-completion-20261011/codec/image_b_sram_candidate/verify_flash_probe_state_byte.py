#!/usr/bin/env python3
"""Bind native flash-state byte accesses to the linked NOLOAD source object."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
TOOL=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
source=ROOT/'g2/components/gx8002/image_b_sram_candidate/backup_stage2_flash_probe_state.c'
consumer=ROOT/'g2/components/gx8002/image_b_sram_candidate/backup_stage2_flash_probe_wait.c'
build=HERE/'build-stock-length-flash-state-byte-round'
elf=build/'image_b_flexible_source_probe.elf'
dis=subprocess.check_output([str(TOOL/'csky-elfabiv2-objdump'),'-D','-b','binary','-m','csky','--adjust-vma=0x10003000','--start-address=0x10007fac','--stop-address=0x10008000',str(stock)],text=True)
for needle in ('10007fc0:', 'r4, 0x2001765c', '10007fc8:',
               'r3, (r4, 0x0)', '10007ff8:', 'r3, 1',
               '10007ffa:'):
    assert needle in dis,needle
listing=subprocess.check_output([str(TOOL/'csky-elfabiv2-nm'),'-S',str(elf)],text=True)
assert '2001765c 00000001 B gx8002_image_b_flash_probe_state_2001765c' in listing
obj=HERE/'build-stage2-flash-state-byte-round/backup_stage2_flash_probe_state.o'
sections=subprocess.check_output([str(TOOL/'csky-elfabiv2-objdump'),'-h',str(obj)],text=True)
assert '.bss.image_b_flash_probe_state 00000001' in sections
assert 'volatile uint8_t gx8002_image_b_flash_probe_state_2001765c' in source.read_text()
assert 'gx8002_image_b_flash_probe_state_2001765c = 1u' in consumer.read_text()
payload=build/'image_b_source_payload.bin'
assert payload.stat().st_size==82060
receipt={'status':'PASS_BOUNDED_FLASH_PROBE_STATE_SOURCE_PLACEMENT',
 'native_stage2_sha256':hashlib.sha256(stock.read_bytes()).hexdigest(),
 'selected_elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'consumer_sha256':hashlib.sha256(consumer.read_bytes()).hexdigest(),
 'native_literal':'0x2001765c','native_read':'0x10007fc8 byte',
 'native_write':'0x10007ffa byte value 1','source_address':'0x2001765c',
 'source_object_bytes':1,'source_storage':'NOBITS/NOLOAD',
 'stock_transfer_payload_bytes':payload.stat().st_size,
 'limits':['Native and selected code both read a byte and write value 1 at the fixed RAM address.',
           'Cold CRT clears the containing BSS range conditionally; warm retained value and a producer of value 2 remain unqualified.',
           'This is a source placement and native access check, not flash device, loader alias, or hardware proof.']}
(build/'flash-state-byte-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
