#!/usr/bin/env python3
"""Bounded native/C UART transport I/O, no waiters and zero timeout."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 objs=[]
 for name in ('transport_io','ring_transfer','ring_available','ring_copy','byte_copy'):
  o=Path(td)/(name+'.o');objs.append(str(o))
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
 stubs=Path(td)/'bounded.c'
 stubs.write_text('''#include <stdint.h>
void offline_assert(void){for (;;) {}}
uint32_t audio_port_mask_set(void){return 0;}
void audio_port_mask_restore(uint32_t x){(void)x;}
void stock_scheduler_suspend(void){}
int32_t stock_scheduler_resume(void){return 0;}
int32_t uart_notify_isr(void*a,uint32_t b,uint32_t c,uint32_t d,uint32_t*e,int32_t*f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t audio_notify_task(void*a,uint32_t b,uint32_t c,uint32_t d,uint32_t*e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void *receiver_current_task(void){return 0;}
uint32_t audio_uart_wait_clear(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_notify_wait(uint32_t a,uint32_t b,uint32_t c,uint32_t*d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
''')
 o=Path(td)/'bounded.o';objs.append(str(o))
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(stubs),'-o',str(o)],check=True)
 elf=Path(td)/'candidate.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(elf),*objs],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,read,cap,head,tail,request,threshold,waiter,frame_length=None):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for addr,data in segs:u.mem_write(addr,data)
  if native:
   def bypass_scheduler(uc,address,size,user):
    if address in (0x454d7c,0x454dcc,0x5fa0a4,0x5fa0ba,
                   0x455dc0,0x455c48):
     uc.reg_write(A.UC_ARM_REG_R0,0)
     uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,bypass_scheduler)
  d=0x20040000;buf=0x20041000;store=0x20042000
  for off,val in ((0,head),(4,tail),(8,cap),(12,threshold),
                  (16,0x20044000 if waiter and not read else 0),
                  (20,0x20044000 if waiter and read else 0),(24,store)):
   u.mem_write(d+off,val.to_bytes(4,'little'))
  u.mem_write(buf,bytes((i*13+7)&255 for i in range(128)))
  u.mem_write(store,bytes((i*17+11)&255 for i in range(128)))
  if frame_length is not None:
   u.mem_write(d+28,b'\x01')
   for i,byte in enumerate(frame_length.to_bytes(4,'little')):
    u.mem_write(store+(head+i)%cap,bytes([byte]))
  address=(0x57e136 if read else 0x57e05e) if native else syms['audio_uart_transport_receive' if read else 'audio_uart_transport_write']
  for reg,val in ((A.UC_ARM_REG_R0,d),(A.UC_ARM_REG_R1,buf),(A.UC_ARM_REG_R2,request),(A.UC_ARM_REG_R3,0 if read else 0x20043000),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101ff1)):
   u.reg_write(reg,val)
  u.emu_start(address|1,0x101ff0,count=4000)
  return (u.reg_read(A.UC_ARM_REG_R0),u.mem_read(d,36),u.mem_read(buf,128),u.mem_read(store,128))
 n=0
 for read in (False,True):
  for cap,head,tail in ((16,0,6),(16,5,10),(32,10,20),(32,28,3)):
   for request in (0,1,2,4):
    for threshold in (0,cap+1):
     for waiter in (False,True):
      if not read and waiter and threshold!=0:continue
      a=run(True,read,cap,head,tail,request,threshold,waiter)
      b=run(False,read,cap,head,tail,request,threshold,waiter)
      assert a==b,(read,cap,head,tail,request,threshold,waiter,a[0],b[0])
      n+=1
 for cap in (16,32):
  for head in (0,3,cap-3):
   for frame_length in (1,2,4,6):
    tail=(head+4+frame_length)%cap
    a=run(True,True,cap,head,tail,8,cap+1,False,frame_length)
    b=run(False,True,cap,head,tail,8,cap+1,False,frame_length)
    assert a==b,('framed-read',cap,head,frame_length,a[0],b[0])
    n+=1
 print('PASS_AUDIO_UART_TRANSPORT_IO',n)
