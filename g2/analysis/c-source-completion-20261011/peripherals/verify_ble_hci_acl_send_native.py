#!/usr/bin/env python3
"""Actual ARM C/native HciSendAclData queue and no-connection effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_acl_send.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0x100];uint8_t audio_ble_hci_stack_state_20073870[0x100];uint8_t *test_conn;
uint8_t *audio_ble_hci_conn_by_handle(uint16_t h){(void)h;return test_conn;}
void audio_ble_wsf_message_free(void*x){(void)x;}
void WsfMsgEnq(void*q,uint8_t h,void*x){(void)h;uint32_t*p=q;uint32_t v=(uint32_t)(uintptr_t)x;p[0]=v;p[1]=v;}
uint16_t WsfQueueCount(const void*q){(void)q;return 1;}
void audio_ble_hci_tx_ready(uint8_t x){(void)x;}
uint16_t audio_ble_hci_get_buf_size(void){return 64;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,HciSendAclData',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case in ('missing','queue'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sym['audio_ble_hci_controller_state_20071478'] if compiled else 0x20071478
   conn=0x20080000;packet=0x20080100
   u.mem_write(state,bytes(0x100));u.mem_write(state+0x80,b'\xff');u.mem_write(conn,bytes(0x1c))
   u.mem_write(packet,b'\x34\x12\x20\x00'+bytes(28))
   if compiled:u.mem_write(sym['test_conn'],(conn if case=='queue' else 0).to_bytes(4,'little'))
   else:
    def hook(uc,pc,n,user):
     if pc==0x52a704:uc.reg_write(UC_ARM_REG_R0,conn if case=='queue' else 0)
     elif pc==0x4bf9de:
      q=uc.reg_read(UC_ARM_REG_R0);p=uc.reg_read(UC_ARM_REG_R2)
      uc.mem_write(q,p.to_bytes(4,'little')*2)
     elif pc==0x538cf6:uc.reg_write(UC_ARM_REG_R0,1)
     elif pc==0x530d34:uc.reg_write(UC_ARM_REG_R0,64)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x52a704,0x4bf9b0,0x4bf9de,0x538cf6,0x530d34):
     u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,packet);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['HciSendAclData'] if compiled else 0x52ad04)|1,0x600000,count=5000)
   pair.append((bytes(u.mem_read(state+0x70,0x14)),bytes(u.mem_read(conn,0x1c))))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_HCI_ACL_SEND_NATIVE 2')
