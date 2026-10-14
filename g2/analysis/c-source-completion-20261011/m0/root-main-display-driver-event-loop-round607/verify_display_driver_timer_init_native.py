#!/usr/bin/env python3
"""Compare Apollo display-driver timer initializer with compiled C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_timer_init.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_uart_timer_new','display_driver_timer_callback_473b54','audio_log_flags',
        'audio_log_extended','compressed_log_output']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global display_driver_timer_handle\ndisplay_driver_timer_handle:\n.space 4\n')
 image=d/'timer.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_init_473ad0',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  cb=next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='display_driver_timer_control_block')
  assert cb['st_size']==44 and elf.get_section(cb['st_shndx']).name=='.bss'
 for result in (0,0x20001234):
  for flags in (0,1,2,4,5,6,7):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    timer=(syms['audio_uart_timer_new'] if compiled else 0x4493b0)&~1
    logflags=(syms['audio_log_flags'] if compiled else 0x43d0ce)&~1
    text=(syms['audio_log_extended'] if compiled else 0x43d574)&~1
    compact=(syms['compressed_log_output'] if compiled else 0x43ce9e)&~1
    calls=[]
    def cs(u,p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
    def hook(u,addr,_size,_user):
     if addr==timer:
      callback=u.reg_read(UC_ARM_REG_R0);kind=u.reg_read(UC_ARM_REG_R1)
      arg=u.reg_read(UC_ARM_REG_R2);attrs=u.reg_read(UC_ARM_REG_R3)
      assert (callback,kind,arg)==((syms['display_driver_timer_callback_473b54'] if compiled else 0x473b55),1,0)
      name=int.from_bytes(u.mem_read(attrs,4),'little')
      flag=int.from_bytes(u.mem_read(attrs+4,4),'little')
      cbptr=int.from_bytes(u.mem_read(attrs+8,4),'little')
      size=int.from_bytes(u.mem_read(attrs+12,4),'little')
      assert (cs(u,name),flag,size)==('display_device_timer',0,44)
      assert cbptr==(syms['display_driver_timer_control_block'] if compiled else 0x200735cc)
      calls.append('timer')
      u.reg_write(UC_ARM_REG_R0,result)
     elif addr==logflags:u.reg_write(UC_ARM_REG_R0,flags);calls.append('flags')
     elif addr==text:
      sp=u.reg_read(UC_ARM_REG_SP)
      assert u.reg_read(UC_ARM_REG_R0)==1
      assert cs(u,u.reg_read(UC_ARM_REG_R1))=='task.displaydrvmgr'
      assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='display_device_resource_init'
      assert int.from_bytes(u.mem_read(sp,4),'little')==0x9f
      assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))=='display_device_timer_id create failed..\r\n'
      calls.append('text')
     elif addr==compact:
      assert u.reg_read(UC_ARM_REG_R0)==0x04000000
      expected='[task.displaydrvmgr]display_device_timer_id create failed..\r\n'
      assert cs(u,u.reg_read(UC_ARM_REG_R1))==expected
      assert cs(u,u.reg_read(UC_ARM_REG_R2))==expected
      calls.append('compact')
     else:return
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.emu_start((syms['display_driver_init_473ad0'] if compiled else 0x473ad0)|1,0x600000,count=300)
    slot=syms['display_driver_timer_handle'] if compiled else 0x200744f0
    value=int.from_bytes(cpu.mem_read(slot,4),'little')
    observations.append((calls,value))
   assert observations[0]==observations[1],(result,flags,observations)
print('PASS_DISPLAY_DRIVER_TIMER_INIT_NATIVE',2*7)
