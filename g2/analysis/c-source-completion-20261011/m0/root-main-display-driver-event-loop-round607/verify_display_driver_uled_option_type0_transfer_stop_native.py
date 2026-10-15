#!/usr/bin/env python3
"""Compare transfer stop return codes, register writes, and state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('void display_driver_uled_transfer_prepare_stop_538d18(unsigned *p){(void)p;}\n')
 image=Path(directory)/'stop.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_transfer_stop.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for function in ('wait','shutdown'):
  for variant in ('null','invalid','inactive','active','mismatch'):
   for force in (0,1) if function=='shutdown' else (0,):cases.append((function,variant,force))
 for function,variant,force in cases:
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   for base,data in segments:u.mem_write(base,data)
   data=bytearray(64)
   def word(offset,value):data[offset:offset+4]=value.to_bytes(4,'little')
   word(0,0x01cdcdcd|(0x02000000 if variant in ('active','mismatch') else 0))
   if variant=='invalid':word(0,0)
   word(28,1);word(32,2 if variant=='mismatch' else 1);word(36,0x20004000)
   u.mem_write(0x20001000,bytes(data))
   for a,v in ((0x20004000,0x20005000),(0x20004010,0x20005004),(0x20004014,0xf0),(0x20005000,0xffffffff),(0x20005004,0xffffffff)):
    u.mem_write(a,v.to_bytes(4,'little'))
   calls=[]
   def lower(uc,at,size,user):
    calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   target=(syms['display_driver_uled_transfer_prepare_stop_538d18']&~1) if compiled else 0x538d18
   u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0 if variant=='null' else 0x20001000);u.reg_write(UC_ARM_REG_R1,force)
   name='display_driver_uled_wait_lower_538e8c' if function=='wait' else 'display_driver_uled_shutdown_lower_53909a'
   native=0x538e8c if function=='wait' else 0x53909a
   u.emu_start((syms[name] if compiled else native)|1,0x600000,count=1000)
   observations.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20001000,64)),bytes(u.mem_read(0x20005000,8))))
  assert observations[0]==observations[1],(function,variant,force,observations[0][:2],observations[1][:2])
 print('PASS_ULED_OPTION_TYPE0_TRANSFER_STOP_NATIVE',len(cases))
