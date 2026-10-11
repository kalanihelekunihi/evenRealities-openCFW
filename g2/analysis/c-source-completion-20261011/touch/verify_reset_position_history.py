#!/usr/bin/env python3
"""Verify typed position history pointer/count plus native widget contracts."""
from pathlib import Path
import hashlib,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-position-history-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_position_history.c';obj=OUT/'history.o';elf=OUT/'history.elf';ld=OUT/'layout.ld';data=OUT/'history.bin'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { .header 0x20000848 : { *(.touch_init.position_history) } .position 0x200009dc (NOLOAD) : { *(.touch_bss.slider_history_position) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
subprocess.run(['arm-none-eabi-objcopy','--dump-section','.header='+str(data),str(elf)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=fw.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
assert len(data.read_bytes())==8 and data.read_bytes()==b[32+0xb914-0x3300:32+0xb91c-0x3300]
wd=32+0xb188-0x3300
assert struct.unpack_from('<I',b,wd+60)[0]==0x20000848
assert struct.unpack_from('<I',b,wd+112)[0]==0x00800102
assert struct.unpack_from('<I',b,wd+48)[0]&3==1
assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
r={'status':'PASS_TYPED_POSITION_HISTORY_HEADER_EIGHT_BYTES','source_sha256':sha(src),'firmware_sha256':sha(fw),'elf_sha256':sha(elf),'bytes':8,'ram':'0x20000848','rom':'0xb914','closed_reset_bytes':480,'remaining_reset_bytes':484,'limits':['Bounded typed data placement and single-position consumer contract.','Wider generated storage allocation, final linker placement and hardware operation remain open.']}
(HERE/'reset-position-history-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
