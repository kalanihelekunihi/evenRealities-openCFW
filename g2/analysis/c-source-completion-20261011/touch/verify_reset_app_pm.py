#!/usr/bin/env python3
"""Compare typed application PM descriptor/threshold and true native return leaf."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-app-pm-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_app_pm.c'
obj=OUT/'pm.o';elf=OUT/'pm.elf';ld=OUT/'layout.ld'
ld.write_text('SECTIONS { .text 0x3620 : { *(.text*) } .descriptor 0x200004cc : { *(.touch_init.app_pm_descriptor) } .threshold 0x200004e8 : { *(.touch_init.app_threshold) } .params 0x200009c0 (NOLOAD) : { *(.touch_bss.app_pm_params) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }\n')
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=fw.read_bytes()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
comparisons=[]
for name,address,length in [('.text',0x3620,4),('.descriptor',0xb598,28),('.threshold',0xb5b4,2)]:
 p=OUT/(name[1:]+'.bin')
 subprocess.run(['arm-none-eabi-objcopy','--dump-section',name+'='+str(p),str(elf)],check=True)
 assert p.read_bytes()==b[32+address-0x3300:32+address-0x3300+length]
 comparisons.append({'section':name,'stock_rom':hex(address),'bytes':length,'sha256':sha(p)})
assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
r={'status':'PASS_TYPED_APP_PM_28_BYTES_THRESHOLD_2_BYTES_CALLBACK_4_BYTES','source_sha256':sha(src),'firmware_sha256':sha(fw),'elf_sha256':sha(elf),'comparisons':comparisons,'closed_reset_bytes':461,'remaining_reset_bytes':503,'limits':['Bounded data and callback placement; final firmware layout and physical PM behavior remain open.','Callback is the authenticated return-zero leaf, not a substitute provider.','Two bytes after the threshold are not counted without allocation/padding ownership.']}
(HERE/'reset-app-pm-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
