"""Actual ARM C/native HCI ACL TxReady queue/credit transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_tx_ready.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xb0];
void *audio_ble_wsf_message_peek(void*q,uint8_t*h){uint32_t head=*(uint32_t*)q;if(!head)return 0;*h=*(uint8_t*)(head+4);return (void*)(head+8);}
void *audio_ble_wsf_message_dequeue(void*q,uint8_t*h){uint32_t head=*(uint32_t*)q;if(!head)return 0;*h=*(uint8_t*)(head+4);*(uint32_t*)q=0;*((uint32_t*)q+1)=0;return (void*)(head+8);}
void audio_ble_wsf_message_free(void*p){(void)p;}
uint8_t *audio_ble_hci_conn_by_handle(uint16_t h){(void)h;return 0;}
uint32_t audio_ble_hci_tx_acl_continue(void*p){(void)p;return 0;}
uint32_t audio_ble_hci_tx_acl_start(void*c,uint16_t n,void*p){(void)c;(void)n;(void)p;return 0;}
void audio_ble_hci_tx_acl_complete(void*c,void*p){(void)c;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_tx_ready_body',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'continue':0x52a8b0,'conn':0x52a704,'start':0x52a850,'complete':0x52a936,'dequeue':0x4bf9ec,'free':0x4bf9b0}
 compiled={'continue':syms['audio_ble_hci_tx_acl_continue']&~1,'conn':syms['audio_ble_hci_conn_by_handle']&~1,'start':syms['audio_ble_hci_tx_acl_start']&~1,'complete':syms['audio_ble_hci_tx_acl_complete']&~1,'dequeue':syms['audio_ble_wsf_message_dequeue']&~1,'free':syms['audio_ble_wsf_message_free']&~1}
 for label,credit,queued,known,accepted in (('zero',0,False,False,False),('saturate',3,False,False,False),('missing',0,True,False,False),('rejected',0,True,True,False),('sent',0,True,True,True)):
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   u.mem_write(state,b'\x00'*0xb0);u.mem_write(state+0x82,b'\x01\x02')
   header=0x20006000;u.mem_write(header,struct.pack('<II',0,0x33)+struct.pack('<HH',2,7)+bytes(20))
   if queued:u.mem_write(state+0x70,struct.pack('<II',header,header))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,credit);u.reg_write(UC_ARM_REG_R2,0x12345678)
   cuts={v:k for k,v in (compiled if is_c else native).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name);val=0
    if name=='conn':val=0x20007000 if known else 0
    elif name=='start':
     val=1 if accepted else 0
     if accepted:uc.mem_write(state+0x82,b'\x00')
    elif name=='dequeue':
     uc.mem_write(state+0x70,b'\x00'*8);uc.mem_write(uc.reg_read(UC_ARM_REG_R1),b'\x33');val=header+8
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_tx_ready_body'] if is_c else 0x52a79e)|1,0x600000,count=550)
   rows.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,bytes(u.mem_read(state+0x70,8)),bytes(u.mem_read(state+0x82,2))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][:3])
