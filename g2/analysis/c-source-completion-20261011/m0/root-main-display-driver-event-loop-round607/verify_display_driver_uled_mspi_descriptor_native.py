#!/usr/bin/env python3
"""Compare descriptor words and return codes for Apollo 0x4bfa3c."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned g2_main_mspi_queue_flags_4bfa10(unsigned a,unsigned b){return 0;}\n')
 image=Path(directory)/'descriptor.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_descriptor.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(compiled,kind,module,length,bad,config):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  h=0x20001000;t=0x20002000;d=0x20003000
  u.mem_write(h,bytes(0x900));u.mem_write(t,bytes(32));u.mem_write(d,bytes([0xa5])*64)
  put(u,h+4,module);u.mem_write(h+13,b'\x03');put(u,h+0x838,config)
  put(u,t,length);put(u,t+4,length);put(u,t+8,0x12345678);put(u,t+12,0x89abcdef);put(u,t+16,bad);put(u,t+20,0xface9876)
  u.mem_write(t+18,bytes([bad&0xff]))
  calls=[]
  def lower(uc,at,size,user):
   a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1)
   calls.append((a,b));uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  at=syms['g2_main_mspi_queue_flags_4bfa10']&~1 if compiled else 0x4bfa10
  u.hook_add(UC_HOOK_CODE,lower,begin=at,end=at)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in ((UC_ARM_REG_R0,h),(UC_ARM_REG_R1,kind),(UC_ARM_REG_R2,d),(UC_ARM_REG_R3,t)):u.reg_write(reg,value)
  u.emu_start((syms['display_driver_uled_mspi_descriptor_4bfa3c'] if compiled else 0x4bfa3c)|1,0x600000,count=1000)
  return calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(d,64))
 cases=0
 for kind in (0,1,2,255,256,257):
  for module in (0,1,7):
   for length in (0,0x1234,0x10000,0x1000000):
    for bad,config in ((0,0),(1,0),(0,1),(1,1)):
     native=run(False,kind,module,length,bad,config);source=run(True,kind,module,length,bad,config)
     assert native==source,((kind,module,length,bad,config),native[:2],source[:2],native[2].hex(),source[2].hex())
     cases+=1
 print('PASS_ULED_MSPI_DESCRIPTOR_NATIVE',cases)
