#!/usr/bin/env python3
"""Composed native/C oracle for snapshot, queue lock, and IRQ save."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
sources=('display_driver_uled_mspi_dma_queue_snapshot_release.c',
         'display_driver_uled_mspi_dma_queue_lock.c','display_driver_uled_irq_save.c')
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'queue-composed.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',*[str(here/x) for x in sources],
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_queue_snapshot_53901a')
 cases=0
 for kind in ('null','bad','valid'):
  for out_kind in ('null','valid'):
   for queue_count in (0,1,0xff,0x100):
    for producer in (0,1,0xfe,0xff):
     for primask in (0,1):
      observations=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       u.mem_map(0x40060000,0x10000)
       for base,data in segments:u.mem_write(base,data)
       q=0 if kind=='null' else 0x20080000
       out=0 if out_kind=='null' else 0x20083000
       set32(u,0x20080000,0x01cdcdcd if kind=='valid' else 0xdeadbeef)
       set32(u,0x20080010,0x20);set32(u,0x20080014,0x10)
       set32(u,0x20080020,queue_count);set32(u,0x20080024,0x20082000)
       set32(u,0x20082004,0x20084000);set32(u,0x20082008,0x20084004)
       set32(u,0x20082018,0x40060200)
       set32(u,0x2008201c,0x1880);set32(u,0x20082020,0x40);set32(u,0x20082024,1)
       set32(u,0x20084000,0x12345678);set32(u,0x20084004,producer)
       set32(u,0x40060200,0x18c1)
       u.mem_write(0x20083000,b'\xcc'*16)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_PRIMASK,primask)
       u.reg_write(UC_ARM_REG_R0,q);u.reg_write(UC_ARM_REG_R1,out)
       u.emu_start((sym if compiled else 0x53901a)|1,0x600000,count=3000)
       observations.append((u.reg_read(UC_ARM_REG_R0),
         u.reg_read(UC_ARM_REG_PRIMASK),
         bytes(u.mem_read(0x20080000,40)),bytes(u.mem_read(0x20083000,16))))
      assert observations[0]==observations[1],(kind,out_kind,queue_count,producer,primask,observations)
      cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_QUEUE_COMPOSED_NATIVE',cases)
