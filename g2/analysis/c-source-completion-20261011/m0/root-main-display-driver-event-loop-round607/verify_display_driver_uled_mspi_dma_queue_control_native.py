#!/usr/bin/env python3
"""Native/C oracle for Apollo DMA queue start/stop 0x538e3c/0x538e8c."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_mspi_dma_queue_start_538e3c',0x538e3c),
         ('display_driver_uled_mspi_dma_queue_stop_538e8c',0x538e8c)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'queue.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_queue_control.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for kind in ('null','bad','valid'):
   for running in (False,True):
    for queue_address in (0x20070000,0x20080000,0x40060000):
     for reg_value in (0,0x12345678,0xffffffff):
      observed=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       u.mem_map(0x40060000,0x10000)
       for base,data in segments:u.mem_write(base,data)
       q=0 if kind=='null' else 0x20080000
       flag=0x02000000 if running else 0
       set32(u,0x20080000,(0x01cdcdcd if kind=='valid' else 0xdeadbeef)|flag)
       set32(u,0x20080008,queue_address)
       set32(u,0x20080024,0x20081000)
       set32(u,0x20081000,0x40060200)
       set32(u,0x40060200,reg_value)
       writes=[]
       def on_write(_u,access,where,size,value,_user):
        if 0x40060000<=where<0x40070000:writes.append((where,size,value))
       u.hook_add(UC_HOOK_MEM_WRITE,on_write)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_R0,q)
       u.emu_start((syms[name] if compiled else address)|1,0x600000,count=1000)
       observed.append((u.reg_read(UC_ARM_REG_R0),
          bytes(u.mem_read(0x20080000,40)),
          bytes(u.mem_read(0x40060200,4)),writes))
      assert observed[0]==observed[1],(name,kind,running,queue_address,reg_value,observed)
      cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_DMA_QUEUE_CONTROL_NATIVE',cases)
