"""Bounded ARM compiled C/native HCI command-status and ACL-credit effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRCS=[ROOT/'components/audio/uart_thread_source_candidate'/n for n in ('display_ble_hci_event_command_children.c','display_ble_hci_acl_children.c')]
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xb0],audio_ble_hci_stack_state_20073870[0x40];
void *audio_wsf_msg_alloc(uint16_t n){(void)n;return 0;}
void audio_ble_hci_cmd_status_failure(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_ble_hci_cmd_receive_complete(uint32_t a){(void)a;}
void audio_ble_hci_tx_ready(uint8_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_num_complete_packets',*[str(x) for x in SRCS],str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'audio_ble_hci_cmd_status_failure':0x56b100,'audio_ble_hci_cmd_receive_complete':0x52aef8,'audio_ble_hci_tx_ready':0x52a79e}
 for label in ('status_ok','status_fail','credits_notify','credits_no_notify','credits_unknown'):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   stack=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   u.mem_write(state,b'\x00'*0xb0);u.mem_write(stack,b'\x00'*0x40)
   u.mem_write(state+0x10,struct.pack('<H',2 if label!='credits_unknown' else 3))
   u.mem_write(state+0x17,b'\x01');u.mem_write(state+0x18,b'\x0a\x0a');u.mem_write(state+0x81,b'\x08')
   u.mem_write(stack+0x14,struct.pack('<I',0x100701))
   pbuf=0x20005000;data=bytearray(12)
   if label.startswith('status'):
    data[0]=0 if label=='status_ok' else 5;data[1]=2;struct.pack_into('<H',data,2,0x2018)
    entry=syms['audio_ble_hci_event_cmd_status'] if is_c else 0x56b150
   else:
    data[0]=1;struct.pack_into('<H',data,1,2);data[3]=3 if label!='credits_no_notify' else 1
    entry=syms['audio_ble_hci_num_complete_packets'] if is_c else 0x530c08
   u.mem_write(pbuf,bytes(data));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,pbuf)
   calls=[];cuts={syms[k]&~1:k for k in native} if is_c else {v:k for k,v in native.items()}
   def hook(uc,a,size,_):
    if a==0x100700:
     calls.append(('notify',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name.endswith('failure') else 0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start(entry|1,0x600000,count=600)
   results.append((calls,bytes(u.mem_read(state+0x10,0x10))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0][0])
