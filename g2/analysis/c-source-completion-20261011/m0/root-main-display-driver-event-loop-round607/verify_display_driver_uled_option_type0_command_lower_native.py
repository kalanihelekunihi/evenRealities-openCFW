#!/usr/bin/env python3
"""Compare native and C mode byte and 28-byte command descriptor."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned display_driver_uled_type0_packet_write_59ccdc(const void *p) {(void)p; return 0;}\n')
 image=Path(directory)/'lower.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_command_lower.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in (0,1,2,255):
  for command,length in ((0,0),(6,0),(0x36,2),(0x46,1),(0x1ff,0x1234)):
   outputs=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    u.mem_write(0x20075024,bytes((mode,)));u.mem_write(0x20074524,(0x11223344).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms['display_driver_uled_mode_45a568'] if compiled else 0x45a568)|1,0x600000,count=100)
    observed_mode=u.reg_read(UC_ARM_REG_R0)
    captured=[]
    def copy(uc,at,size,user):
     dest,source,n=(uc.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
     uc.mem_write(dest,bytes(uc.mem_read(source,n)));uc.reg_write(UC_ARM_REG_R0,dest);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def write(uc,at,size,user):
     captured.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),28)))
     uc.reg_write(UC_ARM_REG_R0,0x12345678)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    if not compiled:u.hook_add(UC_HOOK_CODE,copy,begin=0x439c04,end=0x439c04)
    target=(syms['display_driver_uled_type0_packet_write_59ccdc']&~1) if compiled else 0x59ccdc
    u.hook_add(UC_HOOK_CODE,write,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,command);u.reg_write(UC_ARM_REG_R1,0x20001000);u.reg_write(UC_ARM_REG_R2,length)
    u.emu_start((syms['display_driver_uled_command_5926ee'] if compiled else 0x5926ee)|1,0x600000,count=1000)
    outputs.append((observed_mode,captured,u.reg_read(UC_ARM_REG_R0)))
   assert outputs[0]==outputs[1],(mode,command,length,outputs)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_COMMAND_LOWER_NATIVE',cases)
