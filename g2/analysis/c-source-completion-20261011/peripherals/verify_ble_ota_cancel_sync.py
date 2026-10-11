"""Actual ARM compiled-C/native OTA cancel and status message comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_ota_cancel_sync.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ota_export_state[0x60];
volatile uint8_t audio_ble_ota_sync_enabled,audio_ble_ota_sync_status;
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_ble_send_status_message(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_disconnect',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,enabled,status,flags in (('sync',0,0,0),('sync',0,1,0),('sync',0,2,0),('sync',1,1,0),('cancel',0,1,0),('sync',0,1,7)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_ota_export_state'] if compiled else 0x20072730
   u.mem_write(state,b'X'*0x60)
   u.mem_write(syms['audio_ble_ota_sync_enabled'] if compiled else 0x20074ff3,bytes([enabled]))
   u.mem_write(syms['audio_ble_ota_sync_status'] if compiled else 0x20075024,bytes([status]))
   u.reg_write(UC_ARM_REG_R0,7 if kind=='sync' else 0)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={(syms['audio_uart_buffer_zero']&~1 if compiled else 0x43c0e4):'fill',
         (syms['audio_log_flags']&~1 if compiled else 0x43d0ce):'flags',
         (syms['audio_log_extended']&~1 if compiled else 0x43d574):'log',
         (syms['compressed_log_output']&~1 if compiled else 0x43ce9e):'compact',
         (syms['audio_ble_send_status_message']&~1 if compiled else 0x464d1c):'send'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='fill':uc.mem_write(r0,bytes(uc.reg_read(UC_ARM_REG_R1)));res=r0
    elif k=='flags':res=flags
    elif k in ('log','compact'):
     calls.append((k,r0,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),12)).split(b'\0')[0]));res=0
    else:
     ptr=uc.reg_read(UC_ARM_REG_R1)
     calls.append((r0,bytes(uc.mem_read(ptr,8)),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)));res=0
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   start=(syms['audio_ble_rpc_ota_status_sync'] if compiled else 0x444e90) if kind=='sync' else (syms['audio_ble_ota_disconnect'] if compiled else 0x448784)
   u.emu_start(start|1,0x600000,count=1800)
   rows.append((calls,bytes(u.mem_read(state,0x60)) if kind=='cancel' else b''))
  assert rows[0]==rows[1],(kind,enabled,status,flags,rows)
  print('PASS',kind,enabled,status,flags,len(rows[0][0]))
