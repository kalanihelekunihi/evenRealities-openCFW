"""Actual C/native privacy startup ordering and ten row addresses."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_rows[2000];
void audio_ble_privacy_cache_maintenance(const void*p,uint8_t v){(void)p;(void)v;}
void audio_ble_privacy_load_rows(uint8_t*p){(void)p;}
void audio_ble_subsystem_child_479418(void){}
void audio_ble_privacy_dump_row(uint8_t*p,uint8_t i){(void)p;(void)i;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_other_handler_start',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_start.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 obs=[]
 for c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  base=syms['audio_ble_privacy_rows'] if c else 0x20067a30
  cuts={syms['audio_ble_privacy_cache_maintenance']&~1:'cache',syms['audio_ble_privacy_load_rows']&~1:'load',syms['audio_ble_subsystem_child_479418']&~1:'resolve',syms['audio_ble_privacy_dump_row']&~1:'dump'} if c else {0x475014:'cache',0x4795dc:'load',0x479418:'resolve',0x4789b0:'dump'}
  calls=[]
  def hook(uc,a,size,_):
   if a in cuts:
    calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0)-base if cuts[a] in ('load','dump') else (uc.reg_read(UC_ARM_REG_R0) if cuts[a]=='cache' else None),uc.reg_read(UC_ARM_REG_R1) if cuts[a] in ('cache','dump') else None))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['audio_ble_other_handler_start'] if c else 0x47a85c)|1,0x600000,count=5000)
  obs.append(calls)
 assert obs[0]==obs[1],obs
 print('PASS privacy startup',len(obs[0]),'ordered calls')
