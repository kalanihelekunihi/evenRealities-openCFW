"""Actual compiled-C/native slave service state registration cases, logs disabled."""
from pathlib import Path
import subprocess,struct,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
volatile uint8_t audio_ble_msgtx_handler_id;uint8_t *audio_ble_msgtx_state,*audio_ble_msgtx_mode;
const uint8_t *audio_ble_msgtx_table_slot;const uint8_t audio_ble_msgtx_table[8]={0};
uint8_t audio_ble_ota_handler_state[4],audio_ble_eus_handler_state[4],audio_ble_ess_handler_state[4],audio_ble_efs_handler_state[4],audio_ble_nus_handler_state[4];
void audio_ble_ota_reset_export_state(void){}uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ess_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_slave_service_inits.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,native,cell in [('audio_ble_eus_handler_init',0x4bdf98,0x200748ac),('audio_ble_ess_handler_init',0x4be2d6,0x200748a8),('audio_ble_efs_handler_init',0x4be524,0x200748a4),('audio_ble_nus_handler_init',0x4be7fa,0x200748b0)]:
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   address=syms[name.replace('_init','_state')] if compiled else cell;u.mem_write(address,b'\xa5\xa5\xa5\xa5');cuts={(syms['audio_log_level']&~1 if compiled else 0x43d0ce):'level',(syms['audio_log_extended']&~1 if compiled else 0x43d574):'ext',(syms['compressed_log_output']&~1 if compiled else 0x43ce9e):'compact'}
   def hook(uc,a,size,_):
    if cuts.get(a)=='level':uc.reg_write(UC_ARM_REG_R0,0)
    if a in cuts:uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms[name] if compiled else native)|1,0x600000,count=200)
   obs.append(bytes(u.mem_read(address,4)))
  assert obs[0]==obs[1],(name,obs);print('PASS service init',name)
