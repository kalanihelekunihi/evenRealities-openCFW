"""Actual ARM C/native HCI command queue send transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_cmd_send.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_cmd_state_20073a90[0x40];
void audio_wsf_msg_enqueue(void*q,uint8_t h,void*m){(void)q;(void)h;(void)m;}
void *audio_ble_wsf_message_dequeue(void*q,uint8_t*h){(void)q;(void)h;return 0;}
void audio_ble_wsf_message_free(void*m){(void)m;}
void audio_ble_hci_timer_start_sec(void*t,uint32_t n){(void)t;(void)n;}
uint32_t audio_ble_hci_transport_send_cmd(const void*m){(void)m;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_cmd_send_body',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'timer':0x52a4b8,'transport':0x530166,'dequeue':0x4bf9ec,'free':0x4bf9b0,'enqueue':0x4bf9de}
 compiled={'timer':syms['audio_ble_hci_timer_start_sec']&~1,'transport':syms['audio_ble_hci_transport_send_cmd']&~1,'dequeue':syms['audio_ble_wsf_message_dequeue']&~1,'free':syms['audio_ble_wsf_message_free']&~1,'enqueue':syms['audio_wsf_msg_enqueue']&~1}
 for label,ready,queued,success in (('not_ready',0,True,True),('empty',1,False,True),('send_failed',1,True,False),('sent',1,True,True),('enqueue',0,False,False)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_cmd_state_20073a90'] if is_c else 0x20073a90
   u.mem_write(state,b'\x00'*0x40);u.mem_write(state+0x1a,bytes([ready]))
   if queued:
    u.mem_write(state+0x10,struct.pack('<II',0x20006000,0x20006000))
    u.mem_write(0x20006000,struct.pack('<II',0,0)+struct.pack('<H',0x2018)+bytes(30))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20006008 if label=='enqueue' else 0);u.reg_write(UC_ARM_REG_R2,0x12345678)
   cuts={v:k for k,v in (compiled if is_c else native).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    if name=='dequeue':
     uc.mem_write(state+0x10,b'\x00'*8);uc.reg_write(UC_ARM_REG_R0,0x20006008)
    else:uc.reg_write(UC_ARM_REG_R0,1 if name=='transport' and success else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_cmd_send_body'] if is_c else 0x52ae5e)|1,0x600000,count=350)
   results.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,bytes(u.mem_read(state+0x10,0x0c))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0][:3])
