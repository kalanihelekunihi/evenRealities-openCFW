#!/usr/bin/env python3
"""Bounded native/source SPOT transition outer control flow and return ABI."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[4]
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as folder:
 t=Path(folder);obj=t/'source.o';elf=t/'source.elf';raw=t/'source.bin'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c99','-O2','-ffreestanding','-fno-builtin','-c',str(R/'g2/components/bootloader/source_candidate_20261010/event_a_transition_children.c'),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','event_a_temperature_transition_separate',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(raw)],check=True)
 symbols={parts[2]:int(parts[0],16)&~1 for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(parts:=line.split())>=3}
 for target,current in [(3,1),(1,3),(2,2)]:
  pair=[]
  for original in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x10000,0x1000);u.mem_map(0x410000,0x25000);u.mem_map(0x20000000,0x2000)
   u.mem_write(0x10000,raw.read_bytes());u.mem_write(0x410000,stock)
   u.mem_write(0x20000158+3*4,struct.pack('<I',0x10301))
   lower=0x42a2b4 if original else symbols['event_a_state_transition_sequence']
   calls=[];callback=[];done=[]
   def hook(machine,pc,size,_):
    if pc==lower:
     to_state=machine.reg_read(UC_ARM_REG_R0);from_state=machine.reg_read(UC_ARM_REG_R1);ptr=machine.reg_read(UC_ARM_REG_R2)
     calls.append((to_state,from_state));machine.mem_write(ptr,b'\x03');machine.reg_write(UC_ARM_REG_R0,0);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
    elif pc==0x10300:
     callback.append(tuple(machine.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
     machine.reg_write(UC_ARM_REG_R0,0xdeadbeef);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
    elif pc==0x20001000:done.append(True);machine.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x20001800);u.reg_write(UC_ARM_REG_LR,0x20001001)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(target,current,0x12345678,0xabcdef01)):u.reg_write(reg,val)
   entry=0x42a43a if original else symbols['event_a_temperature_transition_separate']
   try:u.emu_start(entry|1,0x20001002,count=1000)
   except Exception as error:raise AssertionError((original,target,current,error,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_LR)),calls,callback)) from error
   assert done
   pair.append((calls,callback,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_SP)))
  assert pair[0]==pair[1],(target,current,pair)
  print('PASS',target,current,pair[0])
