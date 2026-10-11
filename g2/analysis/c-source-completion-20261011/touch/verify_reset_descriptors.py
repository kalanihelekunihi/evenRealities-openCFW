#!/usr/bin/env python3
"""Compile and compare source-owned Touch slot rows and relocations."""
from pathlib import Path
import hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-reset-descriptors-apollo'
OUT.mkdir(parents=True,exist_ok=True)
FIRMWARE=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
blob=FIRMWARE.read_bytes()
assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
image=blob[32:]
sources=[ROOT/'g2/components/touch/reset_layout_candidate_20261010'/name
         for name in ('reset_sensor_descriptors.c','reset_slot_links.c',
                      'reset_pm_descriptor.c')]
sources.append(ROOT/'g2/components/touch/ilo_pm_offline/pm.c')
objects=[]
for src in sources:
 obj=OUT/(src.stem+'.o')
 subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus',
  '-mthumb','-Og','-ffreestanding','-fno-builtin','-ffunction-sections',
  '-fdata-sections','-Wall','-Wextra','-Werror',
  '-c',str(src),'-o',str(obj)],check=True)
 objects.append(obj)
elf=OUT/'descriptor-islands.elf'
subprocess.run(['arm-none-eabi-ld','-T',str(HERE/'reset_descriptor_islands.ld'),
 '-o',str(elf),*[str(obj) for obj in objects]],check=True)
sections=[('active_slot_link',0xb5e8,4,0x2000051c),
 ('lp_slot_link',0xb5ec,4,0x20000520),
 ('lp_sensor_descriptors',0xb8d4,16,0x20000808),
 ('active_sensor_descriptors',0xb8e4,16,0x20000818),
 ('pm_descriptor',0xb91c,28,0x20000850)]
rows=[]
for name,flash,length,ram in sections:
 out=OUT/(name+'.bin')
 subprocess.run(['arm-none-eabi-objcopy','--dump-section',f'.{name}={out}',str(elf)],check=True)
 data=out.read_bytes();expected=image[flash-0x3300:flash-0x3300+length]
 assert len(data)==length and data==expected,name
 rows.append(dict(section=name,flash_address=hex(flash),ram_address=hex(ram),
                  bytes=length,sha256=hashlib.sha256(data).hexdigest()))
receipt=dict(status='PASS_PARTIAL_SOURCE_ISLANDS',firmware_sha256=hashlib.sha256(blob).hexdigest(),
 source_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
 source_files=[str(p.relative_to(ROOT)) for p in sources],source_owned_bytes=68,
 sections=rows,limits=['Only two descriptor arrays and their two context pointer fields are source-owned here; the other reset-copy fields remain open.','The section addresses come from a bounded linker fixture, not a final executable Touch image.','Physical touch behavior and the missing generated product CapSense configuration are not established.'])
(HERE/'reset-descriptor-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(status=receipt['status'],source_owned_bytes=68,sections=rows),indent=2))
