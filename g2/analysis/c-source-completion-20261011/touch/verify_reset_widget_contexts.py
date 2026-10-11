#!/usr/bin/env python3
"""Compare typed product widget data and true pointer relocation with stock reset."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-reset-widget-contexts-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_widget_contexts.c'
obj=OUT/'widgets.o';elf=OUT/'widgets.elf'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-T',str(HERE/'reset_widget_islands.ld'),str(obj),'-o',str(elf)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';blob=fw.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
rows=[]
for name,rom,ram,count in [('widgets',0xb614,0x20000548,180),('position',0xb722,0x20000656,8)]:
 p=OUT/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.'+name+'='+str(p),str(elf)],check=True)
 data=p.read_bytes();expect=blob[32+rom-0x3300:32+rom-0x3300+count]
 assert len(data)==count and data==expect,(name,data.hex(),expect.hex())
 rows.append({'section':name,'ram':hex(ram),'rom':hex(rom),'bytes':count,'sha256':sha(p)})
receipt={'status':'PASS_TYPED_WIDGET_DATA_AND_POSITION_RELOCATION','firmware_sha256':sha(fw),'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'elf_sha256':sha(elf),'sections':rows,'new_source_owned_bytes':188,'aggregate_source_owned_reset_bytes':313,'remaining_reset_bytes':651,'vendor_commit':'247a9a0f79eb976f144f5fbeb29488c1c2606517','limits':['Exact bounded initialized data/relocation only; full Touch linker and physical behavior remain open.','Product settings use authenticated stock field values and vendor types; generator inputs are not recovered.']}
(HERE/'reset-widget-context-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
