#!/usr/bin/env python3
"""Compare Apollo uLED startup wrapper with compiled C at cut dependencies."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_uled_init.c')
workspace=Path(__file__).with_name('display_driver_uled_work_buffer.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_ble_hci_radio_mode_state_50938e','display_driver_uled_config_mode_4c9d9c',
        'display_driver_uled_row_callback_4ca2ac','audio_log_flags','audio_log_extended',
        'compressed_log_output','test_driver_init']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global display_driver_uled_instance\ndisplay_driver_uled_instance:\n.space 4\n')
 image=d/'init.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_init_4c9f32',
  str(source),str(workspace),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  workspace_symbol=next(s for s in elf.get_section_by_name('.symtab').iter_symbols()
                        if s.name=='display_driver_uled_work_buffer')
  assert workspace_symbol['st_size']==0x400
  assert (syms['display_driver_uled_work_buffer']&31)==0
 for present in (False,True):
  for mode in (5,6):
   for flags in (0,1,2,4,5,6,7) if not present else (0,):
    observations=[]
    for compiled in (False,True):
     cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
     cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x400000)
     for address,data in segments:cpu.mem_write(address,data)
     cpu.mem_write(0x20001000,bytes([mode]))
     slot=syms['display_driver_uled_instance'] if compiled else 0x20074530
     instance=0x20002000 if present else 0
     cpu.mem_write(slot,instance.to_bytes(4,'little'))
     if present:cpu.mem_write(instance+8,syms['test_driver_init'].to_bytes(4,'little'))
     if not compiled:cpu.mem_write(0x200007b8,(0x20094400).to_bytes(4,'little'))
     targets={((syms[n] if compiled else address)&~1):label for n,address,label in [
      ('audio_ble_hci_radio_mode_state_50938e',0x50938e,'mode'),
      ('display_driver_uled_config_mode_4c9d9c',0x4c9d9c,'config'),
      ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
      ('compressed_log_output',0x43ce9e,'compact')]}
     targets[syms['test_driver_init']&~1]='method'
     calls=[]
     def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
     def hook(u,address,_size,_user):
      label=targets.get(address)
      if label is None:return
      r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
      if label=='mode':
       assert r0==1;u.reg_write(UC_ARM_REG_R0,0x20001000)
      elif label=='config':assert r0==(1 if mode==6 else 0);u.reg_write(UC_ARM_REG_R0,0)
      elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
      elif label=='method':
       assert r0==(syms['display_driver_uled_row_callback_4ca2ac'] if compiled else 0x4ca2ad)
       assert r1==0x20094400
       assert u.reg_read(UC_ARM_REG_R2)==(syms['display_driver_uled_work_buffer'] if compiled else 0x203795a0)
       u.reg_write(UC_ARM_REG_R0,0x12345678)
      elif label=='text':
       sp=u.reg_read(UC_ARM_REG_SP)
       assert r0==1 and cs(u,r1)=='driver.uled'
       assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled.c'
       assert cs(u,u.reg_read(UC_ARM_REG_R3))=='uled_mspi_init'
       assert int.from_bytes(u.mem_read(sp,4),'little')==0x90
       assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))=='Error - Failed to find uled driver.\r\n'
      elif label=='compact':
       expected='[driver.uled]Error - Failed to find uled driver.\r\n'
       assert r0==0x04000000 and cs(u,r1)==expected and cs(u,u.reg_read(UC_ARM_REG_R2))==expected
      calls.append(label)
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
     cpu.hook_add(UC_HOOK_CODE,hook)
     cpu.reg_write(UC_ARM_REG_SP,0x203ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
     try:cpu.emu_start((syms['display_driver_init_4c9f32'] if compiled else 0x4c9f32)|1,0x600000,count=300)
     except Exception as exc:raise AssertionError((present,mode,flags,compiled,hex(cpu.reg_read(UC_ARM_REG_PC)))) from exc
     observations.append((calls,cpu.reg_read(UC_ARM_REG_R0)))
    assert observations[0]==observations[1],(present,mode,flags,observations)
print('PASS_DISPLAY_DRIVER_ULED_INIT_NATIVE',2*7+2)
