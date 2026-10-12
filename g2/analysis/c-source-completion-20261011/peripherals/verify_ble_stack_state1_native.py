#!/usr/bin/env python3
"""Valid-range actual compiled-C/native state-one block/crypto effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_state1_5364a4.c'
STUB='''#include <stdint.h>
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){uint8_t*x=d;const uint8_t*y=s;for(uint32_t i=0;i<n;i++)x[i]=y[i];return d;}
void audio_uart_buffer_zero(void*d,uint32_t n,uint32_t v){uint8_t*x=d;for(uint32_t i=0;i<n;i++)x[i]=(uint8_t)v;}
void SecLeEncryptCmd(const uint8_t*k,const uint8_t*p,void*m,uint8_t h){(void)k;(void)p;(void)m;(void)h;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_state1_5364a4',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,offset,length,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;ctx=0x20082000;data=0x20083000
  m=bytearray([0xa5]*64);m[0x30:0x34]=ctx.to_bytes(4,'little')
  for i in range(16):m[16+i]=(seed+i*7)&255
  u.mem_write(msg,bytes(m))
  c=bytearray([0xa5]*48);c[:4]=data.to_bytes(4,'little');c[0x24:0x26]=offset.to_bytes(2,'little');c[0x26:0x28]=length.to_bytes(2,'little');c[0x28]=0x31
  for i in range(16):c[4+i]=(seed+i*11)&255;c[20+i]=(seed+i*13)&255
  u.mem_write(ctx,bytes(c));u.mem_write(data,bytes((seed+i*17)&255 for i in range(64)));trace=[]
  names=[('copy','audio_queue_copy_bytes',0x439be4),('zero','audio_uart_buffer_zero',0x43c0e4),('xor','audio_ble_stack_xor16_542a60',0x542a60),('crypt','SecLeEncryptCmd',0x5363ae)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    p=uc.reg_read(UC_ARM_REG_R0);q=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
    if name=='copy':trace.append(('copy',p,q-data,n));uc.mem_write(p,bytes(uc.mem_read(q,n)))
    elif name=='zero':trace.append(('zero',p,n));uc.mem_write(p,bytes([0])*n)
    elif name=='xor':
     trace.append(('xor',p,q));uc.mem_write(p,bytes(a^b for a,b in zip(uc.mem_read(p,16),uc.mem_read(q,16))))
    else:trace.append(('crypt',bytes(uc.mem_read(p,16)),bytes(uc.mem_read(q,16)),n==msg,uc.reg_read(UC_ARM_REG_R3)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_state1_5364a4'] if compiled else 0x5364a4)|1,0x600000,count=5000)
  normalized=[]
  for item in trace:
   if item[0]=='xor':continue # compiler may inline the exact byte effect
   if item[0] in ('copy','zero'):normalized.append((item[0],item[-1]))
   else:normalized.append(item)
  return bytes(u.mem_read(ctx,48)),normalized
 cases=0
 for offset,length in ((0,0),(0,1),(0,15),(0,16),(0,17),(4,12),(4,20),(4,21)):
  for seed in (0,1,127,255):
   a,b=run(False,offset,length,seed),run(True,offset,length,seed)
   assert a==b,(offset,length,seed,a,b)
   cases+=1
 print('PASS_BLE_STACK_STATE1_NATIVE',cases)
