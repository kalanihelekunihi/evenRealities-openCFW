"""Compiled-C/native flash alignment wrapper return and lower call ABI."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_nvm_records[2560];void audio_ble_privacy_cache_maintenance(void*p,uint8_t v){(void)p;(void)v;}
uint32_t audio_ble_nvm_write_aligned(uint32_t k,const uint8_t*s,uint8_t*d,uint32_t n){(void)k;(void)s;(void)d;(void)n;return 0;}
uint32_t g2_log_exception_number(void){return 0;}int audio_ble_thread_yield(void){return 0;}
uint32_t audio_log_level(void){return 0;}void audio_log_extended(void){}uint32_t compressed_log_output(void){return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_nvm_write_words',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_nvm_write.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for dest,words in ((0x7ff000,32),(0x7ff004,32),(0x7ff000,31)):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   child=(syms['audio_ble_nvm_write_aligned']&~1) if c else 0x4d09d8
   calls=[]
   def hook(uc,a,size,_):
    if a==child:
     calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
     uc.reg_write(UC_ARM_REG_R0,0x42);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x12344321,0x20081000,dest,words)):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_nvm_write_words'] if c else 0x4d0a2c)|1,0x600000,count=500)
   obs.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert obs[0]==obs[1],(dest,words,obs)
  print('PASS NVM alignment',hex(dest),words)
