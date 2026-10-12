#!/usr/bin/env python3
"""Compare compiled C and native ATT client send ownership/queue effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_attc_send_message.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_att_common_state[0x64];
void WsfTaskLock(void){}void WsfTaskUnlock(void){}
uint8_t *audio_ble_attc_ccb_by_conn_id_531820(uint8_t a,uint8_t b){(void)a;(void)b;return 0;}
void audio_ble_attc_exec_callback_531ad6(uint8_t a,uint8_t b,uint16_t c,uint8_t d){(void)a;(void)b;(void)c;(void)d;}
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}void WsfMsgSend(uint8_t a,void*b){(void)a;(void)b;}
void audio_ble_wsf_message_free(void *p){(void)p;}
'''
cases=[(0,0,0,1),(1,0,0,1),(1,100,1,1),(1,5,0,1),(1,100,0,0),(1,100,0,1)]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_attc_send_message_4b5640',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for found,mtu,blocked,allocated in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.mem_write(0x20070000,struct.pack('<I',0x20070100));u.mem_write(0x20070100,struct.pack('<H',mtu)+bytes([4 if blocked else 0]))
   u.mem_write(0x20071000,struct.pack('<H',10)+b'\xaa'*14);u.mem_write(0x20072000,b'\xaa'*12)
   state=sym['audio_ble_att_common_state'] if compiled else 0x200610ac
   u.mem_write(state+0x60,b'\x42')
   trace=[]
   for name,cs,stock in (('lock','WsfTaskLock',0x52b8c8),('ccb','audio_ble_attc_ccb_by_conn_id_531820',0x531820),('unlock','WsfTaskUnlock',0x52b8d0),('callback','audio_ble_attc_exec_callback_531ad6',0x531ad6),('alloc','WsfMsgAlloc',0x4bf99e),('send','WsfMsgSend',0x4bf9ba),('free','audio_ble_wsf_message_free',0x4bf9b0)):
    target=sym[cs] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);c=uc.reg_read(UC_ARM_REG_R2);d=uc.reg_read(UC_ARM_REG_R3)
     if name=='ccb':trace.append((name,a,b));uc.reg_write(UC_ARM_REG_R0,0x20070000 if found else 0)
     elif name=='alloc':trace.append((name,a));uc.reg_write(UC_ARM_REG_R0,0x20072000 if allocated else 0)
     elif name=='callback':trace.append((name,a,b,c,d))
     elif name=='send':trace.append((name,a,b,bytes(uc.mem_read(b,11))))
     elif name=='free':trace.append((name,a))
     else:trace.append((name,))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0x1234);u.reg_write(UC_ARM_REG_R2,4);u.reg_write(UC_ARM_REG_R3,0x20071000)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<I',0));u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_attc_send_message_4b5640'] if compiled else 0x4b5640)|1,0x600000,count=2000)
   pair.append((u.reg_read(UC_ARM_REG_R0),trace))
  assert pair[0]==pair[1],((found,mtu,blocked,allocated),pair)
print('PASS_BLE_ATTC_SEND_MESSAGE_NATIVE',len(cases))
