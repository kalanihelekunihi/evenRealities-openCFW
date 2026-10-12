#!/usr/bin/env python3
"""Original/C queue-drain effects for native RX 0x48f018 and TX 0x475524."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/ble_queue_clear.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_rx_thread_state[16],audio_ble_tx_thread_state[16];
uint32_t audio_cmsis_queue_get_count(void*q){(void)q;return 0;}
int32_t audio_uart_queue_receive(void*q,void*m,uint32_t p,uint32_t t){(void)q;(void)m;(void)p;(void)t;return 0;}
void audio_file_heap_free(void*p){(void)p;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'q.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,Thread_BleMsgrxQueueClear',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,side,messages,fail_at=None,zero_at=None,null_queue=False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for addr,data in seg:u.mem_write(addr,data)
  state=(sy['audio_ble_rx_thread_state'] if side==0 else sy['audio_ble_tx_thread_state']) if is_c else (0x20003ffc if side==0 else 0x20004020)
  queue=0 if null_queue else 0x20050000;u.mem_write(state+12,struct.pack('<I',queue))
  get_addr=(sy['audio_uart_queue_receive']&~1) if is_c else 0x449b3c
  count_addr=(sy['audio_cmsis_queue_get_count']&~1) if is_c else 0x449bc8
  free_addr=(sy['audio_file_heap_free']&~1) if is_c else 0x474d16
  flags_addr=(sy['audio_log_flags']&~1) if is_c else 0x43d0ce
  freed=[];indices=[0]
  def hook(uc,addr,size,user):
   if addr==flags_addr:uc.reg_write(UC_ARM_REG_R0,0)
   elif addr==count_addr:uc.reg_write(UC_ARM_REG_R0,max(0,len(messages)-indices[0]))
   elif addr==get_addr:
    i=indices[0];indices[0]+=1
    if fail_at is not None and i==fail_at:uc.reg_write(UC_ARM_REG_R0,1)
    elif i>=len(messages):uc.reg_write(UC_ARM_REG_R0,1)
    else:
     uc.mem_write(uc.reg_read(UC_ARM_REG_R1),struct.pack('<I',0 if i==zero_at else messages[i]))
     uc.reg_write(UC_ARM_REG_R0,0)
   elif addr==free_addr:freed.append(uc.reg_read(UC_ARM_REG_R0))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  entry=(sy['Thread_BleMsgrxQueueClear'] if side==0 else sy['Thread_BleMsgtxQueueClear']) if is_c else (0x48f018 if side==0 else 0x475524)
  u.emu_start(entry|1,0x600000,count=100000)
  return u.reg_read(UC_ARM_REG_R0),freed,indices[0]
 cases=[([],None,None,True),([],None,None,False),([0x20060000],None,None,False),
        ([0x20060000,0x20060010,0x20060020],None,None,False),
        ([0x20060000,0x20060010],1,None,False),([0x20060000,0x20060010],None,1,False)]
 for side in (0,1):
  for args in cases:
   a=run(False,side,*args);b=run(True,side,*args)
   assert a==b,(side,args,a,b)
 print('PASS_BLE_QUEUE_CLEAR_NATIVE',len(cases)*2)
