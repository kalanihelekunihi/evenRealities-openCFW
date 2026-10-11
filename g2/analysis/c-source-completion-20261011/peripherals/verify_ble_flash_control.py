"""Compiled-C/native HAL callback dispatcher, null and installed paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
typedef uint32_t (*fn)(uint8_t,uint8_t,const uint32_t*);
struct {uintptr_t reserved;fn control;} audio_ble_flash_callbacks;
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_flash_control',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_flash_control.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for installed in (False,True):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   callback=0x600101 if installed else 0
   u.mem_write(0x20073274,struct.pack('<I',callback));u.mem_write(syms['audio_ble_flash_callbacks']+4,struct.pack('<I',callback))
   calls=[]
   def hook(uc,a,size,_):
    if a==0x600100:
     calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
     uc.reg_write(UC_ARM_REG_R0,0x42)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(0x105,0x101,0x20080000)):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_flash_control'] if compiled else 0x480312)|1,0x600000,count=100)
   observations.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert observations[0]==observations[1],(installed,observations)
  print('PASS flash control installed',installed)
