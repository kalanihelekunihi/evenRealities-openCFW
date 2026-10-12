"""Actual ARM C/native timer seconds and HCI command write child comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_cmd_transport.c'
SHIM='''#include <stdint.h>
void audio_ble_wsf_timer_insert(void *p,uint32_t n){(void)p;(void)n;}
uint32_t audio_ble_hci_driver_write(uint32_t a,uint16_t b,const void *p){(void)a;(void)b;(void)p;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_transport_send_cmd',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,n,response in (('timer',0,0),('timer',1,0),('timer',0xffffffff,0),('send',0,3),('send',12,15),('send',12,14)):
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   message=0x20005000;u.mem_write(message,bytes([0,0,n&255])+bytes(13))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R1,n)
   if kind=='timer':entry=syms['audio_ble_hci_timer_start_sec'] if is_c else 0x52a4b8;child=syms['audio_ble_wsf_timer_insert']&~1 if is_c else 0x52a424
   else:entry=syms['audio_ble_hci_transport_send_cmd'] if is_c else 0x530166;child=syms['audio_ble_hci_driver_write']&~1 if is_c else 0x4b4a02
   calls=[]
   def hook(uc,a,size,_):
    if a!=child:return
    calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2) if kind=='send' else 0))
    uc.reg_write(UC_ARM_REG_R0,response);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start(entry|1,0x600000,count=100)
   rows.append((calls,u.reg_read(UC_ARM_REG_R0) if kind=='send' else 0))
  assert rows[0]==rows[1],(kind,n,response,rows)
  print('PASS',kind,n,response,rows[0])
