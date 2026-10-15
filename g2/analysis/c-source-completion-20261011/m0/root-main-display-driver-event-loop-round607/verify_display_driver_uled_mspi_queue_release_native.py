#!/usr/bin/env python3
"""Native/C bounded queue ring-walk oracle for Apollo 0x5390fc."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);image=d/'release.elf'
 (d/'stub.c').write_text('#include <stdint.h>\nuint32_t display_driver_uled_mspi_dma_queue_lock_538d18(uint32_t*q){(void)q;return 0;}\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_queue_snapshot_release.c'),
                 str(d/'stub.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_queue_release_5390fc')
 cases=0
 for kind in ('null','bad','valid'):
  for active in (False,True):
   for layout in ('direct','linear','link'):
    for reg_value in (0,1,0x12345679,0xffffffff):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      u.mem_map(0x40060000,0x10000)
      for base,data in segments:u.mem_write(base,data)
      q=0 if kind=='null' else 0x20080000
      set32(u,0x20080000,(0x01cdcdcd if kind=='valid' else 0xdeadbeef) |
            (0x02000000 if active else 0))
      set32(u,0x20080024,0x20082000)
      set32(u,0x20082000,0x20083000)
      set32(u,0x20082004,0x20084000)
      set32(u,0x20082008,0xabcdef00)
      set32(u,0x20083000,0x40060200 | (reg_value & 1))
      set32(u,0x20084000,0x20085000)
      set32(u,0x40060200,reg_value)
      if layout=='direct':set32(u,0x20085000,0xabcdef01)
      elif layout=='linear':
       set32(u,0x20085000,0x12345678);set32(u,0x20085008,0xabcdef01)
      else:
       set32(u,0x20085000,0x20084000);set32(u,0x20085004,0x20086000)
       set32(u,0x20086000,0xabcdef01)
      writes=[]
      def on_write(_u,access,where,size,value,_user):
       if 0x40060000<=where<0x40070000:writes.append((where,size,value))
      u.hook_add(UC_HOOK_MEM_WRITE,on_write)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,q)
      u.emu_start((sym if compiled else 0x5390fc)|1,0x600000,count=2000)
      observed.append((u.reg_read(UC_ARM_REG_R0),
        bytes(u.mem_read(0x20080000,40)),
        bytes(u.mem_read(0x20083000,4)),
        bytes(u.mem_read(0x20084000,4)),
        bytes(u.mem_read(0x20085000,16)),
        bytes(u.mem_read(0x20086000,4)),
        bytes(u.mem_read(0x40060200,4)),writes))
     assert observed[0]==observed[1],(kind,active,layout,reg_value,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_QUEUE_RELEASE_NATIVE',cases)
