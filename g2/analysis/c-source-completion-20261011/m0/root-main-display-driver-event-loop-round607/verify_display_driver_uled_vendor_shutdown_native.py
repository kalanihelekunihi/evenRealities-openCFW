#!/usr/bin/env python3
"""Compare both native uLED option shutdown callbacks with C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP)
source=Path(__file__).with_name('display_driver_uled_vendor_shutdown.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
children=[('display_driver_uled_mspi_child_4c2392',0x4c2392,'get'),
          ('display_driver_uled_mspi_child_4c23de',0x4c23de,'stop'),
          ('display_driver_uled_mspi_child_4c240e',0x4c240e,'destroy')]
entries=[('display_driver_uled_type1_shutdown_5bbd48',0x5bbd48,
          'display_driver_uled_type1_handle',0x20074510),
         ('display_driver_uled_type0_shutdown_592658',0x592658,
          'display_driver_uled_type0_handle',0x20074524)]
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);stub=d/'stubs.s'
 stub.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {name}\n.thumb_func\n{name}:\n bx lr\n' for name,_,_ in children))
 image=d/'shutdown.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address,cell_name,native_cell in entries:
  for handle in (0,0x20081000):
   for output in (0,0x12345678,0xffffffff):
    for saved_r2 in (0,0x87654321,0xffffffff):
     observations=[]
     for compiled in (False,True):
      cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
      cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
      for base,data in segments:cpu.mem_write(base,data)
      cell=syms[cell_name] if compiled else native_cell
      cpu.mem_write(cell,handle.to_bytes(4,'little'))
      cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
      cpu.reg_write(UC_ARM_REG_R2,saved_r2)
      targets={(syms[n] if compiled else a)&~1:label for n,a,label in children}
      events=[]
      def hook(u,pc,_size,_user):
       label=targets.get(pc)
       if label is None:return
       r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
       if label=='get':
        events.append((label,r0,u.reg_read(UC_ARM_REG_R2)))
        u.mem_write(r1,output.to_bytes(4,'little'))
        u.reg_write(UC_ARM_REG_R0,0x1111)
       else:
        events.append((label,r0,r1))
        u.reg_write(UC_ARM_REG_R0,0x2222 if label=='stop' else 0x3333)
       u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
      cpu.hook_add(UC_HOOK_CODE,hook)
      cpu.emu_start((syms[name] if compiled else address)|1,0x600000,count=90)
      observations.append((events,cpu.reg_read(UC_ARM_REG_R0)))
     assert observations[0]==observations[1],(name,hex(handle),hex(output),hex(saved_r2),observations)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_VENDOR_SHUTDOWN_NATIVE',cases)
