#!/usr/bin/env python3
"""Compare Apollo display-buffer lock's bounded native call paths with ARM C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_prepare_update.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in ('xQueueSemaphoreTake','audio_uart_lvgl_log'))+
  '.bss\n.global display_buffer_semaphore\ndisplay_buffer_semaphore: .space 4\n')
 image=d/'prepare.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for semaphore in (0,0x20088000,0x20088004):
  for take_result in (0,1,0xffffffff):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cell=syms['display_buffer_semaphore'] if compiled else 0x200746bc
    cpu.mem_write(cell,semaphore.to_bytes(4,'little'))
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
     ('xQueueSemaphoreTake',0x441c44,'take'),('audio_uart_lvgl_log',0x44d25c,'log')]}
    events=[]
    def cs(u,p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
    def hook(u,address,_size,_user):
     label=targets.get(address)
     if label is None:return
     if label=='take':
      events.append(('take',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
      u.reg_write(UC_ARM_REG_R0,take_result)
     else:
      sp=u.reg_read(UC_ARM_REG_SP)
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='display_buffer_lock'
      events.append(('log',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R2),
                     cs(u,int.from_bytes(u.mem_read(sp,4),'little'))))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=syms['display_driver_prepare_update_47381e'] if compiled else 0x47381e
    cpu.emu_start(start|1,0x600000,count=100)
    observations.append(events)
   assert observations[0]==observations[1],(semaphore,take_result,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_PREPARE_UPDATE_NATIVE',count)
