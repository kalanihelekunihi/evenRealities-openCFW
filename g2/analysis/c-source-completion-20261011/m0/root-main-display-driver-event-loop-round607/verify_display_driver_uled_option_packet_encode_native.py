#!/usr/bin/env python3
"""Compare S200 packet encoder output with direct native over bounded inputs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('void audio_uart_buffer_zero(void*a,unsigned b,unsigned c){}')
 image=Path(directory)/'encode.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_packet_encode.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for source in (0,0x20001000):
  for output in (0,0x20001100):
   for direction in (0,1,0x123):
    for seed in (0,17):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      u.mem_write(0x20001000,bytes((seed+i*11)&255 for i in range(28)))
      u.mem_write(0x20001100,bytes([0xa5])*24)
      calls=[]
      def lower(uc,at,size,user):
       dst,n,fill=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
       calls.append((n,fill));uc.mem_write(dst,bytes([fill&255])*n)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      target=(syms['audio_uart_buffer_zero']&~1) if compiled else 0x43c0e4
      u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,source);u.reg_write(UC_ARM_REG_R1,output);u.reg_write(UC_ARM_REG_R2,direction)
      u.emu_start((syms['display_driver_uled_packet_encode_59cafc'] if compiled else 0x59cafc)|1,0x600000,count=1000)
      observed.append((calls,bytes(u.mem_read(0x20001100,24))))
     assert observed[0]==observed[1],(source,output,direction,seed,observed)
     cases+=1
 print('PASS_ULED_OPTION_PACKET_ENCODE_NATIVE',cases)
