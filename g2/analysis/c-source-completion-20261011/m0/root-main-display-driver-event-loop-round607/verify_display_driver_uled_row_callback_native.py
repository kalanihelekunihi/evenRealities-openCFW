#!/usr/bin/env python3
"""Compare uLED row fill calls, packed pixels, logging, and return values."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
                               UC_ARM_REG_SP)
source=Path(__file__).with_name('display_driver_uled_row_callback.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
names=[('audio_uart_buffer_zero',0x43c0e4,'fill'),
       ('audio_log_flags',0x43d0ce,'flags'),
       ('audio_log_extended',0x43d574,'text'),
       ('compressed_log_output',0x43ce9e,'compact')]
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);stub=d/'stubs.s'
 stub.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {name}\n.thumb_func\n{name}:\n bx lr\n' for name,_,_ in names)+
  '.data\n.global display_driver_uled_context\n'
  'display_driver_uled_context:\n.word 0x20090000\n')
 image=d/'row.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for start in (0,1,2,3,4,5,638,639):
  for end in (start,start+1,min(639,start+6)):
   if end<640:cases.append((0x5a,start,0,end,1,0))
 cases.extend(((0xa5,0,479,639,480,0),(0x11,638,478,640,479,0),
               (0x37,2,3,1,3,0),(0x37,2,4,2,3,0),
               (0x37,640,0,640,0,0),(0x37,1,480,2,480,0)))
 for flags in (1,2,4,7):cases.append((0x37,10,2,9,2,flags))
 for fill,start_x,start_y,end_x,end_y,flags in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cell=syms['display_driver_uled_context'] if compiled else 0x200007b8
   buffer=0x20090000;cpu.mem_write(cell,buffer.to_bytes(4,'little'))
   cpu.mem_write(buffer,bytes([0xab])*(320*480))
   stack=0x200ff000;cpu.mem_write(stack,end_y.to_bytes(4,'little',signed=True))
   cpu.reg_write(UC_ARM_REG_SP,stack);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in ((UC_ARM_REG_R0,fill),(UC_ARM_REG_R1,start_x),
                   (UC_ARM_REG_R2,start_y),(UC_ARM_REG_R3,end_x)):
    cpu.reg_write(reg,val)
   targets={(syms[name] if compiled else address)&~1:label
            for name,address,label in names}
   events=[]
   def hook(u,address,_size,_user):
    label=targets.get(address)
    if label is None:return
    r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
    if label=='fill':
     value=u.reg_read(UC_ARM_REG_R2)&0xff
     assert buffer<=r0<=buffer+320*480
     assert r0+r1<=buffer+320*480,(start_x,end_x,r0,r1)
     events.append((label,r0-buffer,r1,value))
     u.mem_write(r0,bytes([value])*r1)
    elif label=='flags':
     events.append((label,))
     u.reg_write(UC_ARM_REG_R0,flags)
    elif label=='text':
     events.append((label,))
    else:
     events.append((label,r0))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_uled_row_callback_4ca2ac'] if compiled else 0x4ca2ac
   cpu.emu_start(start|1,0x600000,count=5000)
   observations.append((events,cpu.reg_read(UC_ARM_REG_R0),
                        bytes(cpu.mem_read(buffer,320*480))))
  assert observations[0]==observations[1],(
   fill,start_x,start_y,end_x,end_y,flags,
   observations[0][:2],observations[1][:2])
 print('PASS_DISPLAY_DRIVER_ULED_ROW_CALLBACK_NATIVE',len(cases))
