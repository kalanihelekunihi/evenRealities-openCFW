"""Actual compiled-C/native ANCC initializer memory ranges and lower-call ordering."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x400],audio_ble_ancc_cache[0x400];
uint8_t *audio_ble_ancc_controller,*audio_ble_ancc_mode,*audio_ble_ancc_service_context;
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ble_ancc_reset_state_machine(void){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_profile_ancc_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_ancc_init.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 obs=[]
 for compiled in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  state=syms['audio_ble_ancc_state'] if compiled else 0x200695c8;cache=syms['audio_ble_ancc_cache'] if compiled else 0x2006ddd4
  u.mem_write(state+1,b'\xa5');calls=[]
  cuts={(syms['audio_uart_buffer_zero']&~1 if compiled else 0x43c0e4):'zero',(syms['audio_ble_ancc_reset_state_machine']&~1 if compiled else 0x4bf6c4):'reset'}
  def hook(uc,a,size,_):
   n=cuts.get(a)
   if n=='zero':
    address=uc.reg_read(UC_ARM_REG_R0);base='state' if state<=address<state+0x400 else 'cache';offset=address-(state if base=='state' else cache)
    calls.append((n,base,offset,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
   elif n=='reset':calls.append((n,))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_R2,0x20003000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['audio_ble_profile_ancc_init'] if compiled else 0x4bf742)|1,0x600000,count=250)
  slots=(syms['audio_ble_ancc_controller'],syms['audio_ble_ancc_mode'],syms['audio_ble_ancc_service_context']) if compiled else (0x20074898,0x2007489c,0x200748a0)
  obs.append((u.mem_read(state+1,1)[0],calls,[struct.unpack('<I',u.mem_read(a,4))[0] for a in slots]))
 assert obs[0]==obs[1],obs
 print('PASS ANCC init bytes, zero ranges, pointer roles, reset call')
