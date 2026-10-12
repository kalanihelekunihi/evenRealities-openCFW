#!/usr/bin/env python3
"""Compiled-C/native stack event dispatch, with queue lower effects fixed."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_callback_536234.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[80];
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){uint8_t*x=d;const uint8_t*y=s;for(uint32_t i=0;i<n;i++)x[i]=y[i];return d;}
void WStrReverse(uint8_t*p,uint16_t n){for(unsigned i=0;i<n/2;i++){uint8_t t=p[i];p[i]=p[n-1-i];p[n-1-i]=t;}}
void WsfMsgFree(void*p){(void)p;}
void WsfCsEnter(void){}
void WsfCsExit(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_callback_536234',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,opcode,state,index):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_ble_stack_state_20072cb8'] if compiled else 0x20072cb8
  event=0x20081000;ev=bytearray(range(64));ev[2]=opcode;u.mem_write(event,bytes(ev))
  cells=bytearray([0]*80);cells[0x39]=index
  for s in range(5):cells[0x3c+s*4:0x40+s*4]=(0x1f0301).to_bytes(4,'little')
  messages={}
  for i,off in enumerate((0x20,0x28,0x30)):
   node=0x20082000+i*0x100;messages[off]=node+8
   body=bytearray([0xa5]*88);body[:4]=bytes(4);body[4]=0x42;body[8+0x34]=state;u.mem_write(node,bytes(body))
   cells[off:off+4]=node.to_bytes(4,'little');cells[off+4:off+8]=node.to_bytes(4,'little')
  u.mem_write(base,bytes(cells));trace=[]
  names=[('copy','audio_queue_copy_bytes',0x439be4),('reverse','WStrReverse',0x56d8f0),('free','WsfMsgFree',0x4bf9b0),('csin','WsfCsEnter',0x52b8a4),('csout','WsfCsExit',0x52b8b6)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    p=uc.reg_read(UC_ARM_REG_R0);q=uc.reg_read(UC_ARM_REG_R1)
    if name=='copy':
     size=uc.reg_read(UC_ARM_REG_R2);trace.append(('copy',p-base,q-event,size));uc.mem_write(p,bytes(uc.mem_read(q,size)))
    elif name=='reverse':
     n=q;trace.append(('reverse',p-event,n));uc.mem_write(p,bytes(uc.mem_read(p,n))[::-1])
    elif name=='free':trace.append(('free',p in messages.values()))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  def callback(uc,pc,n,user):
   trace.append(('callback',uc.reg_read(UC_ARM_REG_R0) in messages.values(),uc.reg_read(UC_ARM_REG_R1)==event,uc.reg_read(UC_ARM_REG_R2)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,callback,begin=0x1f0300,end=0x1f0300)
  def invalid(uc,access,address,size,value,user):
   print('INVALID',hex(uc.reg_read(UC_ARM_REG_PC)),hex(address),access,trace[-5:])
   return False
  u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_callback_536234'] if compiled else 0x536234)|1,0x600000,count=5000)
  return bytes(u.mem_read(event,64)),bytes(u.mem_read(base,80)),trace
 cases=0
 for opcode in (0x1c,0x1b,0x25,0x26,0x14,0x99):
  for state in (0,1,3,4):
   for index in (0,3):
    try:a,b=run(False,opcode,state,index),run(True,opcode,state,index)
    except Exception as e:raise AssertionError((opcode,state,index,str(e))) from e
    assert a==b,(opcode,state,index,a,b)
    cases+=1
 print('PASS_BLE_STACK_CALLBACK_536234_NATIVE',cases)
