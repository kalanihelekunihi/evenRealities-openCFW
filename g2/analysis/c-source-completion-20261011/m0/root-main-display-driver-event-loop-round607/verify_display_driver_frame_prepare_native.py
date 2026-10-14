#!/usr/bin/env python3
"""Compare bounded native/C frame descriptor and GPU call sequence."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_frame_prepare.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
providers=[('audio_uart_lvgl_log',0x44d25c,'assert'),
 ('audio_uart_lv_memzero_48949c',0x48949c,'zero'),
 ('audio_uart_checksum_copy',0x439c04,'copy'),
 ('audio_uart_ambiq_bind_buffer_4b092a',0x4b092a,'bind'),
 ('display_driver_gpu_mode_4b0730',0x4b0730,'mode'),
 ('display_driver_gpu_clear_4b1a78',0x4b1a78,'clear'),
 ('display_driver_gpu_enable_4b0748',0x4b0748,'enable'),
 ('display_driver_gpu_blit_4b1608',0x4b1608,'blit'),
 ('display_driver_gpu_position_4b1b48',0x4b1b48,'position'),
 ('audio_uart_ambiq_submit_4b0c8a',0x4b0c8a,'submit'),
 ('audio_log_flags',0x43d0ce,'flags'),
 ('audio_log_extended',0x43d574,'log'),
 ('compressed_log_output',0x43ce9e,'compact')]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_,_ in providers))
 image=d/'frame.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x20094400,0x20080000,640,480,576,288,32,64),
        (0x20094408,0x20080008,64,20,32,8,0,0),
        (0x20094410,0x20080010,100,90,20,10,2,7)]
 count=0
 for args in cases:
  for bind_result in (0,1,2):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):cpu.reg_write(reg,v)
    cpu.mem_write(0x200ff000,b''.join(v.to_bytes(4,'little') for v in args[4:]))
    target={((syms[n] if compiled else addr)&~1):kind for n,addr,kind in providers}
    events=[]
    def hook(u,address,_size,_user):
     kind=target.get(address)
     if kind is None:return
     r=[u.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     if kind=='zero':
      assert r[1]==16;u.mem_write(r[0],bytes(16))
     elif kind=='copy':
      assert r[2]==28;u.mem_write(r[0],bytes(u.mem_read(r[1],28)))
     elif kind=='bind':
      assert r[2]==0
      events.append(('bind',bytes(u.mem_read(r[0],28)).hex(),bytes(u.mem_read(r[1],16)).hex()))
      u.reg_write(UC_ARM_REG_R0,bind_result)
     elif kind=='flags':u.reg_write(UC_ARM_REG_R0,0)
     elif kind in ('assert','log','compact'):raise AssertionError((args,kind))
     elif kind=='blit':
      sp=u.reg_read(UC_ARM_REG_SP)
      events.append((kind,*r,int.from_bytes(u.mem_read(sp,4),'little'),
                     int.from_bytes(u.mem_read(sp+4,4),'little')))
     else:events.append((kind,*r[:2]))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=syms['display_driver_frame_prepare_46c73c'] if compiled else 0x46c73c
    cpu.emu_start(start|1,0x600000,count=500)
    observations.append(events)
   assert observations[0]==observations[1],(args,bind_result,observations)
   count+=1
 guard_cases=[]
 base=[0x20094400,0x20080000,640,480,576,288,32,64]
 for index,value in ((0,0),(1,0),(4,640),(5,480),(6,1),(4,575),
                     (2,639),(0,0x20094401),(1,0x20080001)):
  a=base.copy();a[index]=value;guard_cases.append(a)
 for args in guard_cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):cpu.reg_write(reg,v)
   cpu.mem_write(0x200ff000,b''.join(v.to_bytes(4,'little') for v in args[4:]))
   target=(syms['audio_uart_lvgl_log'] if compiled else 0x44d25c)&~1
   events=[]
   def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
   def hook(u,address,_size,_user):
    if address!=target:return
    sp=u.reg_read(UC_ARM_REG_SP)
    fmt=int.from_bytes(u.mem_read(sp,4),'little')
    condition=int.from_bytes(u.mem_read(sp+4,4),'little')
    events.append((u.reg_read(UC_ARM_REG_R0),cs(u,u.reg_read(UC_ARM_REG_R1)),
      u.reg_read(UC_ARM_REG_R2),cs(u,u.reg_read(UC_ARM_REG_R3)),
      cs(u,fmt),cs(u,condition)))
    u.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_frame_prepare_46c73c'] if compiled else 0x46c73c
   cpu.emu_start(start|1,0x600000,count=200)
   observations.append(events)
  assert observations[0]==observations[1] and len(observations[0])==1,(args,observations)
print('PASS_DISPLAY_DRIVER_FRAME_PREPARE_NATIVE',count,'GUARDS',len(guard_cases))
