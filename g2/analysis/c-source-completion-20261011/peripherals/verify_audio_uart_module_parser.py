#!/usr/bin/env python3
"""Bounded original-byte/C TinyFrame parser states with logging disabled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/module_parser.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 h=Path(td)/'helpers.c'
 h.write_text('''#include <stdint.h>
void audio_uart_parser_frame_done(void*p){(void)p;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 objs=[]
 for n,s in (('parser',S),('strings',S.with_name('module_strings.c')),('helpers',h)):
  o=Path(td)/(n+'.o');objs.append(str(o))
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(s),'-o',str(o)],check=True)
 p=Path(td)/'parser.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),*objs],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,state,value,index,seed,tick,flags=0,length=4):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  m=0x20040000;u.mem_write(m,bytes(0x7160))
  for off,val in ((0x12,tick),(0x14,0x1234),(0x16,length),(0x6018,index),(0x601a,seed),(0x601c,0),(0x601e,0)):
   u.mem_write(m+off,val.to_bytes(2,'little'))
  u.mem_write(m+0x10,bytes([state]))
  calls=[]
  children=({0x43d0ce:'flags',0x4919e8:'done',0x43d574:'extended',0x43ce9e:'compressed'} if native else
            {syms['audio_log_flags']&~1:'flags',syms['audio_uart_parser_frame_done']&~1:'done',
             syms['audio_log_extended']&~1:'extended',syms['compressed_log_output']&~1:'compressed'})
  def string_at(uc,address):
   return bytes(uc.mem_read(address,160)).split(b'\0')[0]
  def cut(uc,address,size,user):
   if address in children:
    kind=children[address]
    if kind=='extended':
     sp=uc.reg_read(A.UC_ARM_REG_SP)
     line=int.from_bytes(uc.mem_read(sp,4),'little')
     message=int.from_bytes(uc.mem_read(sp+4,4),'little')
     calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                   string_at(uc,uc.reg_read(A.UC_ARM_REG_R2)),string_at(uc,uc.reg_read(A.UC_ARM_REG_R3)),
                   line,string_at(uc,message)))
    elif kind=='compressed':
     calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                   string_at(uc,uc.reg_read(A.UC_ARM_REG_R2))))
    else:calls.append(kind)
    uc.reg_write(A.UC_ARM_REG_R0,flags if kind=='flags' else 0)
    uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cut)
  for reg,val in ((A.UC_ARM_REG_R0,m),(A.UC_ARM_REG_R1,value),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101ff1)):
   u.reg_write(reg,val)
  u.emu_start((0x491be4 if native else syms['audio_uart_module_feed_byte'])|1,0x101ff0,count=4000)
  regions=(u.mem_read(m+0x10,16),u.mem_read(m+0x18,8),u.mem_read(m+0x6018,10))
  return regions,calls
 n=0
 for state in range(8):
  for value in (0,1,0x55,0xff):
   for index in (0,1):
    for seed in (0,0x1234):
     for tick in (0,100):
      a=run(True,state,value,index,seed,tick);b=run(False,state,value,index,seed,tick)
      assert a==b,(state,value,index,seed,tick,a,b)
      n+=1
 for seed in (0,0x1234,0xffff):
  for value in range(256):
   a=run(True,1,value,0,seed,0);b=run(False,1,value,0,seed,0)
   assert a==b,('crc',seed,value,a,b)
   n+=1
 for flags in (1,2,4,7):
  for state,index,seed,tick,length in ((1,0,0,100,4),(2,1,0x1234,0,4),
                                        (2,1,0,0,0x6001),(6,1,0x1234,0,4)):
   a=run(True,state,0,index,seed,tick,flags,length)
   b=run(False,state,0,index,seed,tick,flags,length)
   assert a==b,('logs',flags,state,index,seed,tick,length,a,b)
   n+=1
 print('PASS_AUDIO_UART_MODULE_PARSER',n)
