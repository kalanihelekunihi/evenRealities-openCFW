#!/usr/bin/env python3
"""Compare native transfer stop snapshot and IRQ restore state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_PRIMASK
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned display_driver_uled_irq_save_473940(void){return 0;}\n')
 image=Path(directory)/'prepare.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_transfer_prepare_stop.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for saved_mask in (0,1):
  for old,counter in ((0x12340000,0),(0x1234007f,0x80),(0x12340001,0xfe),(0xffffffff,0)):
   observations=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    u.mem_write(0x20001020,old.to_bytes(4,'little'));u.mem_write(0x20001024,(0x20004000).to_bytes(4,'little'))
    for a,v in ((0x20004004,0x20005000),(0x20004008,0x20005004),(0x20005000,0xabcdef12),(0x20005004,counter)):
     u.mem_write(a,v.to_bytes(4,'little'))
    calls=[]
    def lower(uc,at,size,user):
     calls.append('irq_save');uc.reg_write(UC_ARM_REG_R0,saved_mask);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    target=(syms['display_driver_uled_irq_save_473940']&~1) if compiled else 0x473940
    u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20001000)
    u.emu_start((syms['display_driver_uled_transfer_prepare_stop_538d18'] if compiled else 0x538d18)|1,0x600000,count=1000)
    observations.append((calls,bytes(u.mem_read(0x2000100c,4)),bytes(u.mem_read(0x2000101c,4)),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert observations[0]==observations[1],(saved_mask,old,counter,observations)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_TRANSFER_PREPARE_STOP_NATIVE',cases)
