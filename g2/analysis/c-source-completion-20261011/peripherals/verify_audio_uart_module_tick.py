#!/usr/bin/env python3
"""Bounded original-byte/C TinyFrame feed and timer-pump transitions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/module_tick.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 h=Path(td)/'helpers.c';h.write_text('''#include <stdint.h>
void audio_uart_module_feed_byte(void*a,uint8_t b){(void)a;(void)b;}
void audio_uart_module_timer_expire(void*a,uint32_t b,void*c){(void)a;(void)b;(void)c;}
''')
 objs=[]
 for n,s in (('module',S),('helpers',h)):
  o=Path(td)/(n+'.o');objs.append(str(o))
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(s),'-o',str(o)],check=True)
 p=Path(td)/'module.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),*objs],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,pump,slots=0,tick=0,states=(),count=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  module=0x20040000;source=0x20050000;u.mem_write(source,bytes((x*17+3)&255 for x in range(32)))
  u.mem_write(module+0x12,tick.to_bytes(2,'little'));u.mem_write(module+0x7158,bytes([slots]))
  for i,(active,remaining) in enumerate(states):
   base=module+0x6430+i*0x18
   u.mem_write(base+4,active.to_bytes(4,'little'))
   u.mem_write(base+12,remaining.to_bytes(2,'little'))
  traces=[]
  child_addrs=({0x491be4:'feed',0x49183e:'expire'} if native else
               {syms['audio_uart_module_feed_byte']&~1:'feed',syms['audio_uart_module_timer_expire']&~1:'expire'})
  def cut(uc,address,size,user):
   if address in child_addrs:
    traces.append((child_addrs[address],uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_R1),uc.reg_read(A.UC_ARM_REG_R2)))
    uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cut)
  addr=(0x492288 if pump else 0x491b9a) if native else syms['audio_uart_module_pump' if pump else 'audio_uart_module_receive']
  u.reg_write(A.UC_ARM_REG_R0,module);u.reg_write(A.UC_ARM_REG_R1,source)
  u.reg_write(A.UC_ARM_REG_R2,count);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start(addr|1,0x101ff0,count=1000)
  return (u.mem_read(module+0x12,2),[u.mem_read(module+0x6430+i*0x18+12,2) for i in range(slots)],traces)
 n=0
 for count in range(0,17):
  a=run(True,False,count=count);b=run(False,False,count=count)
  # R2 is scratch for byte feed and not caller meaningful; compare byte args.
  assert a[2] and all(x[:3]==y[:3] for x,y in zip(a[2],b[2])) if count else a==b
  assert len(a[2])==len(b[2])==count,(count,a,b)
  n+=1
 for tick in (0,99,100,101,65535):
  for states in (((0,0),),((1,1),),((1,2),),((0,1),(1,1)),((1,2),(1,1),(0,4))):
   a=run(True,True,len(states),tick,states);b=run(False,True,len(states),tick,states)
   assert a==b,(tick,states,a,b)
   n+=1
 print('PASS_AUDIO_UART_MODULE_TICK',n)
