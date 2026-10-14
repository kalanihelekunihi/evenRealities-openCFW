#!/usr/bin/env python3
"""Compare Apollo setters through compiled lock, message packer and queue submit."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 providers=('display_driver_frame_prepare_46c73c','xQueueSemaphoreTake','audio_uart_lvgl_log',
            'audio_uart_buffer_zero','audio_cmsis_queue_put','audio_log_flags',
            'audio_log_extended','compressed_log_output')
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in providers)+
  '.data\n.global audio_settings_display_profile_cell\naudio_settings_display_profile_cell: .word 8\n'
  '.global audio_settings_display_brightness_cell\naudio_settings_display_brightness_cell: .word 64\n'
  '.global display_driver_uled_context\ndisplay_driver_uled_context: .word 0x20094400\n'
  '.bss\n.global display_buffer_semaphore\ndisplay_buffer_semaphore: .space 4\n'
  '.global audio_display_driver_manager\naudio_display_driver_manager: .space 16\n')
 image=d/'chain.elf'
 sources=[here/n for n in ('display_driver_position_setters.c','display_driver_case3_prelude.c',
                          'display_driver_prepare_update.c','display_driver_submit_window.c')]
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',*[str(s) for s in sources],str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 entries=[('display_driver_set_brightness_46c984',0x46c984,[(0,),(255,)]),
          ('display_driver_set_profile_46c9aa',0x46c9aa,[(1,),(0xffffffff,)]),
          ('display_driver_set_offsets_46c9dc',0x46c9dc,
           [(0,0),(48,64),(49,0),(0,65),(16,32)])]
 count=0
 for name,native,cases in entries:
  for args in cases:
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cells=[syms[x] for x in ('audio_settings_display_profile_cell',
           'audio_settings_display_brightness_cell','display_driver_horizontal_offset_cell',
           'display_driver_vertical_offset_cell')] if compiled else [0x20000648,0x2000064c,0x20000650,0x200744c8]
    for a,v in zip(cells,(8,64,24,0)):cpu.mem_write(a,v.to_bytes(4,'little'))
    sem=syms['display_buffer_semaphore'] if compiled else 0x200746bc
    mgr=syms['audio_display_driver_manager'] if compiled else 0x20000658
    cpu.mem_write(sem,(0x20088000).to_bytes(4,'little'))
    cpu.mem_write(mgr+12,(0x20089000).to_bytes(4,'little'))
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):cpu.reg_write(reg,value)
    target={((syms[n] if compiled else addr)&~1):kind for n,addr,kind in [
     ('xQueueSemaphoreTake',0x441c44,'take'),('audio_uart_buffer_zero',0x43c0e4,'zero'),
     ('audio_cmsis_queue_put',0x449abe,'queue'),('audio_uart_lvgl_log',0x44d25c,'lvlog'),
     ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'log'),
     ('compressed_log_output',0x43ce9e,'compact')]}
    calls=[]
    def hook(u,address,_size,_user):
     kind=target.get(address)
     if kind is None:return
     if kind=='take':
      calls.append(('take',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
      u.reg_write(UC_ARM_REG_R0,1)
     elif kind=='zero':
      assert u.reg_read(UC_ARM_REG_R1)==36
      u.mem_write(u.reg_read(UC_ARM_REG_R0),bytes(36))
     elif kind=='queue':
      assert u.reg_read(UC_ARM_REG_R0)==0x20089000
      assert (u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))==(0,1000)
      calls.append(('queue',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),36)).hex()))
      u.reg_write(UC_ARM_REG_R0,0)
     elif kind=='flags':u.reg_write(UC_ARM_REG_R0,0)
     else:raise AssertionError((name,args,kind))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=400)
    observations.append((calls,cpu.reg_read(UC_ARM_REG_R0),
      [int.from_bytes(cpu.mem_read(a,4),'little') for a in cells]))
   assert observations[0]==observations[1],(name,args,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_SETTER_CHAIN_NATIVE',count)
