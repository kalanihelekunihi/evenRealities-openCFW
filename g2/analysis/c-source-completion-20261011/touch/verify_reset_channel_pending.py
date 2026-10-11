#!/usr/bin/env python3
"""Check typed channel and source-owned child relocations in bounded layout."""
from pathlib import Path
import hashlib,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[4]; HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-reset-channel-pending-20261011'; OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_channel_pending.c'
obj=OUT/'channel.o'; data=OUT/'channel.bin'; elf=OUT/'channel.elf'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-objcopy','--dump-section','.touch_init.pending_channel='+str(data),str(obj)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'; blob=fw.read_bytes()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
assert struct.unpack_from('<I',blob,32+0xb2b0-0x3300)[0]==0x2000082c
expected=blob[32+0xb8f8-0x3300:32+0xb8f8-0x3300+28]; actual=data.read_bytes()
assert len(actual)==28
for start,end in [(0,4),(8,24)]: assert actual[start:end]==expected[start:end]
relocations=subprocess.check_output(['arm-none-eabi-readelf','-rW',str(obj)],text=True)
for offset,name in [('00000004','touch_msclp_context_ram_20000cc8'),('00000018','touch_shield_config_rom_b32c')]:
 assert any(offset in line and 'R_ARM_ABS32' in line and name in line for line in relocations.splitlines())
receipt={'status':'PASS_CHANNEL_SCALARS_WITH_TWO_UNRESOLVED_DATA_PROVIDERS','source_sha256':sha(src),'object_sha256':sha(obj),'firmware_sha256':sha(fw),'scalar_bytes_compared':20,'structure_bytes':28,'ram':'0x2000082c','rom':'0xb8f8','provider_addresses':{'touch_msclp_context_ram_20000cc8':'0x20000cc8','touch_shield_config_rom_b32c':'0xb32c'},'selected_by_image_builder':False,'closed_reset_bytes_unchanged':403,'remaining_closed_reset_bytes':561,'limits':['Two source-owned data providers and final relocations remain unresolved.','Scalar comparison does not close all 28 bytes or establish final image layout.']}
script=OUT/'channel.ld'
script.write_text('SECTIONS { .shield_electrodes 0xb32c : { *(.touch_rom.shield_electrodes) } .shield_pins 0xb33c : { *(.touch_rom.shield_pins) } .channel 0x2000082c : { *(.touch_init.pending_channel) } .driver 0x20000cc8 (NOLOAD) : { *(.touch_bss.msclp_context) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(script),str(obj),'-o',str(elf)],check=True)
for section,address,length in [('.channel',0xb8f8,28),('.shield_electrodes',0xb32c,16),('.shield_pins',0xb33c,16)]:
 target=OUT/(section[1:]+'.bin')
 subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(target),str(elf)],check=True)
 assert target.read_bytes()==blob[32+address-0x3300:32+address-0x3300+length]
assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
receipt.update(status='PASS_TYPED_CHANNEL_28_BYTES_AND_ROM_CHILDREN_32_BYTES',elf_sha256=sha(elf),selected_by_image_builder=True,closed_reset_bytes=431,remaining_closed_reset_bytes=533,limits=['Bounded layout verifies initialized data and child pointers; final firmware layout and hardware operation remain open.','Driver lock context is a typed zero-initialized four-byte object outside the reset-copy range.'])
receipt['primary_type_references']=[{'commit':'247a9a0f79eb976f144f5fbeb29488c1c2606517','header':'capsense-v6-reference/cy_capsense_structure.h','sha256':sha(HERE/'capsense-v6-reference/cy_capsense_structure.h')},{'commit':'69bb46becb33da0215576d6d22f6b225165d4c28','header':'g2/analysis/source-discovery-parallel-2026-10-09/pdl-history/69bb46becb33da0215576d6d22f6b225165d4c28/drivers__include__cy_msclp.h','sha256':sha(ROOT/'g2/analysis/source-discovery-parallel-2026-10-09/pdl-history/69bb46becb33da0215576d6d22f6b225165d4c28/drivers__include__cy_msclp.h')}]
receipt.pop('closed_reset_bytes_unchanged')
(HERE/'reset-channel-pending-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
