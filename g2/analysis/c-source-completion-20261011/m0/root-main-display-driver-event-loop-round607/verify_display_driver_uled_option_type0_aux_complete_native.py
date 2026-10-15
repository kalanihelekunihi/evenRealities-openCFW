#!/usr/bin/env python3
"""Compare auxiliary complete register-write and delay sequence with S200 native."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_buffer_zero',0x43c0e4),('display_driver_uled_type0_aux_reg_write_5926ee',0x5926ee),('audio_ble_hci_boot_delay_491102',0x491102),('audio_delay',0x449376)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,at in callees))
 image=Path(directory)/'complete.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_aux_complete.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 observed=[]
 for compiled in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  calls=[]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if name=='audio_uart_buffer_zero':
    calls.append((name,r1,r2));uc.mem_write(r0,bytes(r1))
   elif name=='display_driver_uled_type0_aux_reg_write_5926ee':calls.append((name,r0,r2,bytes(uc.mem_read(r1,20))))
   else:calls.append((name,r0))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for n,at in callees:
   target=syms[n]&~1 if compiled else at
   u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['display_driver_uled_type0_aux_complete_593660'] if compiled else 0x593660)|1,0x600000,count=1000)
  observed.append(calls)
 assert observed[0]==observed[1],observed
 print('PASS_ULED_OPTION_TYPE0_AUX_COMPLETE_NATIVE',len(observed[0]))
