"""Actual ARM C/native HCI connection record allocation and cleanup."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_conn_lifecycle.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xb0];
void audio_ble_wsf_message_free(void *p){(void)p;}
void audio_ble_hci_tx_ready(uint8_t n){(void)n;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_conn_alloc',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,func,initial,attached in (('alloc', 'alloc',0xffff,False),('alloc_full','alloc',2,False),('free_empty','free',2,False),('free_buffers','free',2,True),('free_missing','free',3,False),('open','open',0xffff,False),('close','close',2,True)):
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   u.mem_write(state,b'\x00'*0xb0)
   for i in range(3):u.mem_write(state+i*0x1c+0x10,struct.pack('<H',initial if i==0 else 0xffff if initial==0xffff else 4+i))
   u.mem_write(state+0x17,b'\x01');u.mem_write(state+0x18,b'\x09\x06')
   if attached:u.mem_write(state,struct.pack('<I',0x20006000));u.mem_write(state+8,struct.pack('<I',0x20006100))
   address={'alloc':0x52a67c,'free':0x52a6b0,'open':0x52a758,'close':0x52a762}[func]
   entry=syms['audio_ble_hci_conn_'+func] if is_c else address
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,2)
   free=syms['audio_ble_wsf_message_free']&~1 if is_c else 0x4bf9b0
   ready=syms['audio_ble_hci_tx_ready']&~1 if is_c else 0x52a79e
   calls=[]
   def hook(uc,a,size,_):
    if a==free:calls.append(('free',uc.reg_read(UC_ARM_REG_R0)))
    elif a==ready:calls.append(('ready',uc.reg_read(UC_ARM_REG_R0)))
    else:return
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start(entry|1,0x600000,count=300)
   rows.append((calls,bytes(u.mem_read(state,0x54))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0])
