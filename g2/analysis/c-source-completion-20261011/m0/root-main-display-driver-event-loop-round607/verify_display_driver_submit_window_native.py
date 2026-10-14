#!/usr/bin/env python3
"""Compare Apollo display message packaging and send branches against ARM C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_submit_window.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 names=['audio_uart_buffer_zero','audio_cmsis_queue_put','audio_log_flags',
        'audio_log_extended','compressed_log_output']
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global audio_display_driver_manager\naudio_display_driver_manager: .space 16\n')
 image=d/'submit.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,0,0,0,0x240,0x120),(1,2,3,4,5,6),(0xffffffff,0x80000000,7,8,9,10)]
 count=0
 for args in cases:
  for flags in (0,1,2,4,7):
   for status in (0,1):
    observations=[]
    for compiled in (False,True):
     cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
     cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
     for address,data in segments:cpu.mem_write(address,data)
     manager=syms['audio_display_driver_manager'] if compiled else 0x20000658
     cpu.mem_write(manager+12,(0x20081234).to_bytes(4,'little'))
     cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
     for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):cpu.reg_write(reg,v)
     cpu.mem_write(0x200ff000,b''.join(v.to_bytes(4,'little') for v in args[4:]))
     targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
      ('audio_uart_buffer_zero',0x43c0e4,'zero'),('audio_cmsis_queue_put',0x449abe,'queue'),
      ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
      ('compressed_log_output',0x43ce9e,'compact')]}
     events=[]
     def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
     def hook(u,address,_size,_user):
      label=targets.get(address)
      if label is None:return
      if label=='zero':
       dest=u.reg_read(UC_ARM_REG_R0);size=u.reg_read(UC_ARM_REG_R1)
       assert size==36 and u.reg_read(UC_ARM_REG_R2)==0
       u.mem_write(dest,bytes(size))
      elif label=='queue':
       assert u.reg_read(UC_ARM_REG_R0)==0x20081234
       assert u.reg_read(UC_ARM_REG_R2)==0 and u.reg_read(UC_ARM_REG_R3)==1000
       ptr=u.reg_read(UC_ARM_REG_R1)
       events.append(('queue',bytes(u.mem_read(ptr,36)).hex()))
       u.reg_write(UC_ARM_REG_R0,status)
      elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
      elif label=='text':
       sp=u.reg_read(UC_ARM_REG_SP)
       assert cs(u,u.reg_read(UC_ARM_REG_R1))=='task.displaydrvmgr'
       assert cs(u,u.reg_read(UC_ARM_REG_R3))=='send_async_reflash_msg'
       assert int.from_bytes(u.mem_read(sp,4),'little')==0x161
       events.append(('text',u.reg_read(UC_ARM_REG_R0),cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))))
      elif label=='compact':
       events.append(('compact',u.reg_read(UC_ARM_REG_R0),cs(u,u.reg_read(UC_ARM_REG_R1))))
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
     cpu.hook_add(UC_HOOK_CODE,hook)
     start=syms['display_driver_submit_window_474066'] if compiled else 0x474066
     cpu.emu_start(start|1,0x600000,count=300)
     observations.append((events,cpu.reg_read(UC_ARM_REG_R0)))
    assert observations[0]==observations[1],(args,flags,status,observations)
    count+=1
print('PASS_DISPLAY_DRIVER_SUBMIT_WINDOW_NATIVE',count)
