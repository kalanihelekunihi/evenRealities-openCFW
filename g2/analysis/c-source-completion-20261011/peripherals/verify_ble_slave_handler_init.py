"""Actual compiled-C/native APP_SlaveHanderInit registration and child-call order."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
funcs=[('audio_ble_adv_name_set',0x46dd44),('audio_ble_msgtx_set_config',0x4780dc),('audio_ble_ota_handler_init',0x4bdd00),('audio_ble_eus_handler_init',0x4bdf98),('audio_ble_ess_handler_init',0x4be2d6),('audio_ble_efs_handler_init',0x4be524),('audio_ble_nus_handler_init',0x4be7fa),('audio_ble_profile_ancc_init',0x4bf742)]
shim='''#include <stdint.h>
const uint8_t audio_ble_slave_registration_table[8]={0},audio_ble_slave_profile_table[8]={0};
const uint8_t *audio_ble_slave_registration_slot,*audio_ble_slave_profile_slot;
uint8_t *audio_ble_profile_connection_context,*audio_ble_slave_mode_context,*audio_ble_slave_subcontext;
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''+''.join('void '+n+'('+('void' if i==0 else 'uint8_t a,uint8_t*b,uint8_t*c' if i in (1,7) else 'uint8_t a')+'){'+('' if i==0 else '(void)a;(void)b;(void)c;' if i in (1,7) else '(void)a;')+'}\n' for i,(n,a) in enumerate(funcs))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_app_slave_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_slave_handler_init.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 obs=[]
 for compiled in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[n]&~1 if compiled else a):n for n,a in funcs};cuts.update({(syms['audio_log_level']&~1 if compiled else 0x43d0ce):'level',(syms['audio_log_extended']&~1 if compiled else 0x43d574):'ext',(syms['compressed_log_output']&~1 if compiled else 0x43ce9e):'compact'})
  calls=[]
  def hook(uc,a,size,_):
   n=cuts.get(a)
   if n is None:return
   if n=='level':uc.reg_write(UC_ARM_REG_R0,0)
   elif n not in ('ext','compact'):calls.append((n,uc.reg_read(UC_ARM_REG_R0) if n!='audio_ble_adv_name_set' else 0,uc.reg_read(UC_ARM_REG_R1) if n in ('audio_ble_msgtx_set_config','audio_ble_profile_ancc_init') else 0,uc.reg_read(UC_ARM_REG_R2) if n in ('audio_ble_msgtx_set_config','audio_ble_profile_ancc_init') else 0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  slots=(syms['audio_ble_slave_registration_slot'],syms['audio_ble_slave_profile_slot'],syms['audio_ble_profile_connection_context'],syms['audio_ble_slave_mode_context'],syms['audio_ble_slave_subcontext']) if compiled else (0x2007434c,0x20074350,0x2007432c,0x20074330,0x20074334)
  state=0x20003000;mode=0x20004000;u.mem_write(mode+31,b'\x5a');u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,state);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['audio_ble_app_slave_handler_init'] if compiled else 0x46ed94)|1,0x600000,count=500)
  slotvals=[struct.unpack('<I',u.mem_read(a,4))[0] for a in slots]
  # Normalize addresses of source-owned tables; compare their roles, not relocated numerical addresses.
  slotvals[0]-=(syms['audio_ble_slave_registration_table'] if compiled else 0x200003e0)
  slotvals[1]-=(syms['audio_ble_slave_profile_table'] if compiled else 0x78f6d2)
  obs.append((calls,slotvals,u.mem_read(mode+31,1)[0]))
 assert obs[0]==obs[1],obs
 print('PASS slave handler initializer, registrations and 8 child calls')
