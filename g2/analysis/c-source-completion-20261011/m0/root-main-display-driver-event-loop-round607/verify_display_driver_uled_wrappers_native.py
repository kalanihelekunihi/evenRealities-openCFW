#!/usr/bin/env python3
"""Compare three uLED vtable wrappers against authenticated Apollo native code."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_uled_status.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
rows=[('display_driver_case0',0x4ca18a,0x10,'uled_driver_power_up',0xc8,True),
      ('display_driver_case1_a',0x4ca010,0x0c,'uled_driver_init',0xa4,False),
      ('display_driver_case2',0x4c9fb4,0x1c,'uled_clearScreen',0x9a,False),
      ('display_driver_case5_b',0x4ca126,0x14,'uled_driver_power_down',0xbf,False),
      ('display_driver_case4_apply',0x4ca1ee,0x18,'uled_mspi_setBrightness',0xd1,False),
      ('display_driver_case3',0x4ca564,0x28,'uled_QSPI_PartialReflash_async',0x157,False)]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_log_flags','audio_log_extended','compressed_log_output','test_method']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names))
 image=d/'uled.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_case0',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for name,native,offset,caller,line,power in rows:
  scenarios=[(False,f,False) for f in (0,1,2,4,5,6,7)]+[(True,0,True),(True,7,True)]
  if name in ('display_driver_case0','display_driver_case5_b'):scenarios.append((True,3,False))
  for present,flags,method_present in scenarios:
   count+=1;observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    instance=0x20002000 if present else 0
    slot=syms['display_driver_uled_instance'] if compiled else 0x20074530
    cpu.mem_write(slot,instance.to_bytes(4,'little'))
    if present:
     method=syms['test_method'] if method_present else 0
     cpu.mem_write(instance+offset,method.to_bytes(4,'little'))
    targets={((syms[n] if compiled else addr)&~1):label for n,addr,label in [
      ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
      ('compressed_log_output',0x43ce9e,'compact')]}
    targets[syms['test_method']&~1]='method'
    calls=[]
    def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
    def hook(u,address,_size,_user):
     label=targets.get(address)
     if label is None:return
     r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
     if label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
     elif label=='method':
      if name=='display_driver_case1_a':assert r0==0
      elif name=='display_driver_case4_apply':
       assert (r0,u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2))==(0xabcdef01,0x1234,0x5678)
      elif name=='display_driver_case3':
       assert (r0,u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))==(0xabcdef01,0x1234,0x5678,0x9abc)
       sp=u.reg_read(UC_ARM_REG_SP)
       assert [int.from_bytes(u.mem_read(sp+i*4,4),'little') for i in range(2)]==[0x1111,0x2222]
      else:assert r0==syms['test_method']
      u.reg_write(UC_ARM_REG_R0,0x12345678)
     elif label=='text':
      sp=u.reg_read(UC_ARM_REG_SP)
      expected='Error -no uled device or power_up function, failed.\r\n' if power else 'Error - Failed to find uled driver.\r\n'
      assert r0==1 and cs(u,r1)=='driver.uled'
      assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled.c'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))==caller
      assert int.from_bytes(u.mem_read(sp,4),'little')==line
      assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))==expected
     elif label=='compact':
      expected=('[driver.uled]Error -no uled device or power_up function, failed.\r\n' if power else
                '[driver.uled]Error - Failed to find uled driver.\r\n')
      assert r0==0x04000000 and cs(u,r1)==expected and cs(u,u.reg_read(UC_ARM_REG_R2))==expected
     calls.append(label)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_R0,0xabcdef01)
    cpu.reg_write(UC_ARM_REG_R1,0x1234);cpu.reg_write(UC_ARM_REG_R2,0x5678);cpu.reg_write(UC_ARM_REG_R3,0x9abc)
    cpu.mem_write(0x200ff000,(0x1111).to_bytes(4,"little")+(0x2222).to_bytes(4,"little"))
    cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=300)
    observations.append((calls,cpu.reg_read(UC_ARM_REG_R0)))
   assert observations[0]==observations[1],(name,present,flags,method_present,observations)
print('PASS_DISPLAY_DRIVER_ULED_WRAPPERS_NATIVE',count)
