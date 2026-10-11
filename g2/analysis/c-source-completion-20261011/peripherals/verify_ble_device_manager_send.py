"""Actual compiled-C/native DEV_SendMessage queue and counter transition cases."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_device_manager_state[16];volatile uint8_t audio_ble_device_manager_queue_errors;
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_device_manager_send',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_device_manager_send.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for queue,message,status,counter in ((0,0x20001000,0,0),(0x20002000,0,0,0),(0x20002000,0x20001000,0,4),(0x20002000,0x20001000,7,4),(0x20002000,0x20001000,7,255)):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cell=syms['audio_ble_device_manager_state'] if compiled else 0x2000060c
   ctr=syms['audio_ble_device_manager_queue_errors'] if compiled else 0x20074fb2
   u.mem_write(cell+12,struct.pack('<I',queue));u.mem_write(ctr,bytes([counter]));calls=[]
   cuts={syms['audio_cmsis_queue_put']&~1:'queue',syms['audio_log_level']&~1:'level',syms['audio_log_extended']&~1:'ext',syms['compressed_log_output']&~1:'compact'} if compiled else {0x449abe:'queue',0x43d0ce:'level',0x43d574:'ext',0x43ce9e:'compact'}
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if kind is None:return
    if kind=='queue':calls.append(('queue',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)));uc.reg_write(UC_ARM_REG_R0,status)
    elif kind=='level':uc.reg_write(UC_ARM_REG_R0,0)
    else:calls.append((kind,))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_device_manager_send'] if compiled else 0x4c659a)|1,0x600000,count=500)
   observations.append((calls,u.mem_read(ctr,1)[0]))
  assert observations[0]==observations[1],(queue,message,status,counter,observations)
  print('PASS device send',queue,message,status,counter)
