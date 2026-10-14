#!/usr/bin/env python3
"""Compare Apollo two-option uLED identifier with compiled C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_uled_identify.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_delay','audio_log_flags','audio_log_extended','compressed_log_output']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global display_driver_uled_instance\ndisplay_driver_uled_instance:\n.space 4\n'
  '.global display_driver_uled_option_type1\ndisplay_driver_uled_option_type1:\n.space 64\n'
  '.global display_driver_uled_option_type0\ndisplay_driver_uled_option_type0:\n.space 64\n')
 image=d/'identify.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_uled_config_mode_4c9d9c',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for requested in (0,1,2,256,257):
  for flags in (0,1,2,4,5,6,7):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    option1=syms['display_driver_uled_option_type1'] if compiled else 0x70afe4
    option0=syms['display_driver_uled_option_type0'] if compiled else 0x70b024
    if compiled:
     cpu.mem_write(option1+0x3c,b'\x01');cpu.mem_write(option0+0x3c,b'\x00')
    cell=syms['display_driver_uled_instance'] if compiled else 0x20074530
    cpu.mem_write(cell,b'\0'*4)
    targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
      ('audio_delay',0x449376,'delay'),('audio_log_flags',0x43d0ce,'flags'),
      ('audio_log_extended',0x43d574,'text'),('compressed_log_output',0x43ce9e,'compact')]}
    calls=[];match=requested&0xff in (0,1);index=0 if (requested&0xff)==1 else 1
    def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
    def hook(u,address,_size,_user):
     label=targets.get(address)
     if label is None:return
     r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
     if label=='delay':assert r0==1;u.reg_write(UC_ARM_REG_R0,0)
     elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
     elif label=='text':
      sp=u.reg_read(UC_ARM_REG_SP)
      assert r0==(3 if match else 1) and cs(u,r1)=='driver.uled'
      assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled.c'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='uled_driver_identify'
      assert int.from_bytes(u.mem_read(sp,4),'little')==(0x76 if match else 0x7c)
      expected=('find uled_driver_opt type %d index %d \r\n' if match else ' Error - Failed to find uled_driver_opt.\r\n')
      assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))==expected
      if match:assert [int.from_bytes(u.mem_read(sp+i*4,4),'little') for i in (2,3)]==[requested&0xff,index]
     elif label=='compact':
      assert r0==(0x0c800000 if match else 0x04000000)
      expected=('[driver.uled]find uled_driver_opt type %d index %d \r\n' if match else
                '[driver.uled] Error - Failed to find uled_driver_opt.\r\n')
      assert cs(u,r1)==expected and cs(u,u.reg_read(UC_ARM_REG_R2))==expected
      if match:
       assert u.reg_read(UC_ARM_REG_R3)==requested&0xff
       assert int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4),'little')==index
     calls.append(label)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_R0,requested)
    cpu.emu_start((syms['display_driver_uled_config_mode_4c9d9c'] if compiled else 0x4c9d9c)|1,0x600000,count=500)
    selected=int.from_bytes(cpu.mem_read(cell,4),'little')
    normalized=(1 if selected==option1 else 0 if selected==option0 else None)
    observations.append((calls,cpu.reg_read(UC_ARM_REG_R0),normalized))
   assert observations[0]==observations[1],(requested,flags,observations)
print('PASS_DISPLAY_DRIVER_ULED_IDENTIFY_NATIVE',5*7)
