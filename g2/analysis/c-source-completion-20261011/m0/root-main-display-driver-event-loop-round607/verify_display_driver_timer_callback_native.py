#!/usr/bin/env python3
"""Compare display-driver timer callback message and logs with native Apollo."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_timer_callback.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_uart_buffer_zero','audio_cmsis_queue_put','audio_log_flags','audio_log_extended','compressed_log_output']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global audio_display_driver_manager\naudio_display_driver_manager:\n.space 16\n')
 image=d/'callback.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_timer_callback_473b54',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for result in (0,1):
  for flags in (0,1,2,4,5,6,7):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for addr,data in segments:cpu.mem_write(addr,data)
    manager=syms['audio_display_driver_manager'] if compiled else 0x20000658
    cpu.mem_write(manager+12,(0x20002000).to_bytes(4,'little'))
    targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
      ('audio_uart_buffer_zero',0x43c0e4,'zero'),('audio_cmsis_queue_put',0x449abe,'put'),
      ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
      ('compressed_log_output',0x43ce9e,'compact')]}
    calls=[]
    def cs(u,p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
    def hook(u,addr,_size,_user):
     label=targets.get(addr)
     if label is None:return
     r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
     if label=='zero':
      assert (r1,u.reg_read(UC_ARM_REG_R2))==(36,0)
      u.mem_write(r0,b'\0'*36)
     elif label=='put':
      assert (r0,u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))==(0x20002000,0,1000)
      msg=bytes(u.mem_read(r1,36));assert msg==(6).to_bytes(4,'little')+b'\0'*32
      u.reg_write(UC_ARM_REG_R0,result)
     elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
     elif label=='text':
      sp=u.reg_read(UC_ARM_REG_SP)
      assert r0==2 and cs(u,r1)=='task.displaydrvmgr'
      assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='display_device_timer_callback'
      assert int.from_bytes(u.mem_read(sp,4),'little')==0xb5
      assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))=='async_reflash_xQueue1 send failed..\r\n'
     elif label=='compact':
      assert r0==0x08000000
      expected='[task.displaydrvmgr]async_reflash_xQueue1 send failed..\r\n'
      assert cs(u,r1)==expected and cs(u,u.reg_read(UC_ARM_REG_R2))==expected
     calls.append(label)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_R0,0x12345678)
    cpu.emu_start((syms['display_driver_timer_callback_473b54'] if compiled else 0x473b54)|1,0x600000,count=300)
    observations.append(calls)
   assert observations[0]==observations[1],(result,flags,observations)
print('PASS_DISPLAY_DRIVER_TIMER_CALLBACK_NATIVE',2*7)
