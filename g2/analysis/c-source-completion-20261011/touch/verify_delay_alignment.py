#!/usr/bin/env python3
"""Attribute three reset padding bytes to natural uint32 object alignment."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-delay-alignment-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/source_candidate_20261010/reset_data.c';obj=OUT/'delay.o';elf=OUT/'delay.elf';data=OUT/'delay.bin';ld=OUT/'layout.ld'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
# No explicit fill/ALIGN: the next C uint32_t object's section alignment does it.
ld.write_text('SECTIONS { .delays 0x20000870 : { *(.data.cy_delayFreqMhz) *(.data.cy_delayFreqKhz) } /DISCARD/ : { *(*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
subprocess.run(['arm-none-eabi-objcopy','--dump-section','.delays='+str(data),str(elf)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=fw.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
assert len(data.read_bytes())==8 and data.read_bytes()==b[32+0xb93c-0x3300:32+0xb944-0x3300]
r={'status':'PASS_NATURAL_C_UINT32_ALIGNMENT_THREE_BYTES','source_sha256':sha(src),'elf_sha256':sha(elf),'firmware_sha256':sha(fw),'ram':'0x20000870','compared_bytes':8,'previously_closed_scalar_bytes':5,'newly_closed_alignment_bytes':3,'closed_reset_bytes':472,'remaining_reset_bytes':492,'limits':['Bounded ordered source data section, not final firmware map.','This is natural alignment between two attributed C objects, not an arbitrary zero-filled stock gap.']}
(HERE/'delay-alignment-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
