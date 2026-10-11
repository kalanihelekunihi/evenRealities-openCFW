"""Actual compiled-C/native callback WSF message layout, with logger and WSF cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t *audio_ble_master_context,*audio_ble_controller;
void *audio_wsf_msg_alloc(uint16_t a){(void)a;return 0;}void audio_wsf_msg_send(uint8_t a,void*b){(void)a;(void)b;}
uint32_t audio_log_level(void){return 0;}void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_disconnect_delayed',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_connect_callbacks.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for fn,native,arg,ready,alloc in [('audio_ble_master_disconnect_delayed',0x4a01fc,0x1234,1,1),('audio_ble_master_success_delayed',0x4bc418,0x0123,0,1),('audio_ble_master_success_delayed',0x4bc418,0x0123,1,0),('audio_ble_master_success_delayed',0x4bc418,0x0123,1,1)]:
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   if compiled:u.mem_write(syms['audio_ble_master_context'],struct.pack('<I',0x20002000));u.mem_write(syms['audio_ble_controller'],struct.pack('<I',0x20002100))
   else:u.mem_write(0x200742fc,struct.pack('<I',0x20002000));u.mem_write(0x200727f0,struct.pack('<I',0x20002100))
   u.mem_write(0x20002056,b'\x07');u.mem_write(0x20002156,bytes([7 if ready else 0]));u.mem_write(0x20003000,b'\xaa'*12)
   cuts={(syms[n]&~1 if compiled else addr):n for n,addr in [('audio_wsf_msg_alloc',0x4bf99e),('audio_wsf_msg_send',0x4bf9ba),('audio_log_level',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]};calls=[]
   if not compiled:cuts[0x4b8122]='controller'
   def hook(uc,a,size,_):
    n=cuts.get(a)
    if n is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if n=='audio_wsf_msg_alloc':calls.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,0x20003000 if alloc else 0)
    elif n=='audio_wsf_msg_send':calls.append(('send',r0,bytes(uc.mem_read(r1,12))))
    elif n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='controller':uc.reg_write(UC_ARM_REG_R0,0x20002100)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms[fn] if compiled else native)|1,0x600000,count=500)
   obs.append(calls)
  assert obs[0]==obs[1],(fn,ready,alloc,obs)
  print('PASS callback',fn,ready,alloc)
