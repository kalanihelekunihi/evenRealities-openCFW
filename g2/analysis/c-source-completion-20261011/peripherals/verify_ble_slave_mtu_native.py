#!/usr/bin/env python3
"""Actual compiled-C/native slave MTU parent, with child call contracts held equal."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_mtu.c'
STUB='''#include <stdint.h>
uint8_t *audio_ble_slave_mode_context;
uint8_t *audio_ble_att_ccb_by_conn_id(uint8_t c){(void)c;return 0;}
uint8_t *attMsgAlloc(uint16_t n){(void)n;return 0;}
void *audio_ble_attc_send_message_4b5640(uint8_t a,uint16_t b,uint8_t c,void*d,uint8_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_request_mtu',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,conn,mtu):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  event=0x20081000;row=0x20082000;u.mem_write(event,conn.to_bytes(2,'little'));u.mem_write(row,bytes([0xa5]*64))
  cell=sy['audio_ble_slave_mode_context'] if compiled else 0x20074330
  u.mem_write(cell,row.to_bytes(4,'little'));trace=[]
  names=[('get','audio_ble_att_get_mtu',0x4b5204),('req','audio_ble_attc_mtu_request',0x4b57fa),('log','audio_log_level',0x43d0ce)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    if name=='get':trace.append(('get',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,mtu)
    elif name=='req':trace.append(('req',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,0)
    else:uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x87654321)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_slave_request_mtu'] if compiled else 0x46dedc)|1,0x600000,count=2000)
  return bytes(u.mem_read(row,64)),trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)
 cases=0
 for conn in (0,1,0x12,0xff,0x1234):
  for mtu in (23,0xf7,0x1234,0xffff):
   a,b=run(False,conn,mtu),run(True,conn,mtu)
   assert a==b,(conn,mtu,a,b)
   cases+=1
 print('PASS_BLE_SLAVE_MTU_NATIVE',cases)
