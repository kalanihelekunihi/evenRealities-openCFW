#!/usr/bin/env python3
"""Direct stock/C live image-row selector effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_image_rows.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('#include <stdint.h>\nuint32_t audio_ble_radio_io_mode_52dd1c(uint32_t x){(void)x;return 0;}')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_image_rows_52e788',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for mode in (0,1,7):
  for a,b,c,d in ((0,0,0,0),(2,0x20001234,3,0x20005678),(255,0xffffffff,254,0x12345678)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for x,y in segments:u.mem_write(x,y)
    for addr,value,size in ((0x20074f50,a,1),(0x2007422c,b,4),(0x20074f52,c,1),(0x2007423c,d,4)):u.mem_write(addr,value.to_bytes(size,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in ((UC_ARM_REG_R0,0x2007a000),(UC_ARM_REG_R1,0x2007a004),(UC_ARM_REG_R2,0xface),(UC_ARM_REG_R3,0xdeadbeef)):u.reg_write(reg,value)
    target=(sym['audio_ble_radio_io_mode_52dd1c']&~1) if is_c else 0x52dd1c
    def hook(uc,addr,size,_):
     if addr==target:uc.reg_write(UC_ARM_REG_R0,mode);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_radio_image_rows_52e788'] if is_c else 0x52e788)|1,0x600000,count=250)
    pair.append((bytes(u.mem_read(0x2007a000,8)),u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(mode,a,b,c,d,pair)
   count+=1
 print('PASS_RADIO_IMAGE_ROWS_NATIVE',count)
