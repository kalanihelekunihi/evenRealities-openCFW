"""Compiled-C/native aligned NVM wrapper with authentic lower calls cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R9,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_ble_flash_enter_program_mode(void){}void audio_ble_flash_leave_program_mode(void){}
uint32_t audio_ble_flash_execute(uint32_t k,uint32_t m,const uint8_t*s,uint32_t off,uint32_t n){(void)k;(void)m;(void)s;(void)off;(void)n;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_nvm_write_aligned',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_nvm_aligned.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for dest,ret in ((0x7ff000,0),(0x7ff000,5),(0x7ff001,0)):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cuts={syms['audio_ble_flash_enter_program_mode']&~1:'enter',syms['audio_ble_flash_execute']&~1:'execute',syms['audio_ble_flash_leave_program_mode']&~1:'leave'} if c else {0x473940:'irq_save',0x47f3c6:'enter',0x541b7c:'execute',0x47f418:'leave'}
   calls=[]
   def hook(uc,a,size,_):
    if c and a==(syms['audio_ble_nvm_write_aligned']&~1)+0x1e: # Normalize PRIMASK save/CPSID.
     uc.reg_write(UC_ARM_REG_R9,0)
     uc.reg_write(UC_ARM_REG_PC,a+7)
     return
    if c and a==(syms['audio_ble_nvm_write_aligned']&~1)+0x48: # Normalize PRIMASK restore.
     uc.reg_write(UC_ARM_REG_PC,a+5)
     return
    if not c and a==0x4d0a14: # Unicorn does not emulate native MSR PRIMASK.
     uc.reg_write(UC_ARM_REG_PC,0x4d0a19)
     return
    if a in cuts:
     kind=cuts[a]
     if kind=='irq_save':
      uc.reg_write(UC_ARM_REG_R0,0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      return
     if kind=='execute':
      sp=uc.reg_read(UC_ARM_REG_SP);n=struct.unpack('<I',uc.mem_read(sp,4))[0]
      calls.append((kind,tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)),n))
      uc.reg_write(UC_ARM_REG_R0,ret)
     else:calls.append((kind,))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x12344321,0x20081000,dest,32)):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   try:u.emu_start((syms['audio_ble_nvm_write_aligned'] if c else 0x4d09d8)|1,0x600000,count=1000)
   except Exception as exc:raise AssertionError((c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
   obs.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert obs[0]==obs[1],(dest,ret,obs)
  print('PASS aligned NVM',hex(dest),ret)
