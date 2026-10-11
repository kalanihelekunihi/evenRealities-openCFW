#!/usr/bin/env python3
"""Bounded original-byte/C TinyFrame frame dispatch and timer listeners."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=R/'g2/components/audio/uart_thread_source_candidate'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 h=Path(td)/'helpers.c';h.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void audio_uart_module_timer_expire(void*a,uint32_t b,void*c){(void)a;(void)b;(void)c;}
''')
 objs=[]
 for n,s in (('dispatch',D/'module_dispatch.c'),('strings',D/'module_strings.c'),('helpers',h)):
  o=Path(td)/(n+'.o');objs.append(str(o));subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(s),'-o',str(o)],check=True)
 p=Path(td)/'dispatch.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),*objs],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,kind,result,slot):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  m=0x20040000;u.mem_write(m,bytes(0x7160))
  for off,val in ((0x14,0x1234),(0x16,3),(0x601e,0x5678)):
   u.mem_write(m+off,val.to_bytes(2,'little'))
  if kind=='timer':
   t=m+0x6430+slot*0x18;u.mem_write(m+0x7158,bytes([slot+1]))
   for off,val,size in ((0,0x1234,2),(4,0x101101,4),(12,5,2),(14,7,2),(16,0x34567890,4),(20,0x13579bdf,4)):
    u.mem_write(t+off,val.to_bytes(size,'little'))
  elif kind=='type':
   t=m+0x7030+slot*8;u.mem_write(m+0x7159,bytes([slot+1]));u.mem_write(t,(0x5678).to_bytes(2,'little'));u.mem_write(t+4,(0x101101).to_bytes(4,'little'))
  elif kind=='global':
   t=m+0x7130+slot*4;u.mem_write(m+0x715a,bytes([slot+1]));u.mem_write(t,(0x101101).to_bytes(4,'little'))
  calls=[]
  hooks=({0x43d0ce:'flags',0x101100:'handler',0x49183e:'expire'} if native else
         {syms['audio_log_flags']&~1:'flags',0x101100:'handler',
          syms['audio_uart_module_timer_expire']&~1:'expire'})
  def cut(uc,address,size,user):
   if address in hooks:
    what=hooks[address]
    if what=='handler':
     rec=uc.reg_read(A.UC_ARM_REG_R1)
     calls.append((what,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(rec,24))))
     uc.reg_write(A.UC_ARM_REG_R0,result)
    elif what=='expire':
     calls.append((what,uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_R1),
                   uc.reg_read(A.UC_ARM_REG_R2)))
     uc.reg_write(A.UC_ARM_REG_R0,0)
    else:
     calls.append((what,));uc.reg_write(A.UC_ARM_REG_R0,0)
    uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cut)
  u.reg_write(A.UC_ARM_REG_R0,m);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x4919e8 if native else syms['audio_uart_parser_frame_done'])|1,0x101ff0,count=2000)
  return (u.mem_read(m+0x6430,0x18*(slot+1)),u.mem_read(m+0x7030,8*(slot+1)),u.mem_read(m+0x7130,4*(slot+1)),u.mem_read(m+0x7158,3),calls)
 n=0
 for kind in ('none','timer','type','global'):
  for slot in (0,1):
   for result in (0,1,2,3):
    a=run(True,kind,result,slot);b=run(False,kind,result,slot)
    assert a==b,(kind,result,slot,a,b)
    n+=1
 print('PASS_AUDIO_UART_MODULE_DISPATCH',n)
