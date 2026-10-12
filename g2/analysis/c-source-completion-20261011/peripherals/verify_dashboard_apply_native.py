#!/usr/bin/env python3
"""Bounded original/C comparison of native 0x502174 layout assembly.

Diagnostics disabled. Layout setter intercepted on both sides; this verifies
the argument bytes, fallback behavior, and return for defined protobuf inputs.
"""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
volatile uint8_t audio_uart_dashboard_ready;
uint8_t audio_uart_dashboard_decoded[188];
const char audio_uart_dashboard_module[]="x",audio_uart_dashboard_source[]="y";
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_dashboard_layout_set(const void *p){(void)p;return 0;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){uint8_t*b=p;for(uint32_t i=0;i<n;i++)b[i]=(uint8_t)v;}
void *audio_dashboard_copy_limited(void *d,const void *s,uint32_t n){uint8_t*a=d;const uint8_t*b=s;uint32_t i=0;for(;i<n&&b[i];i++)a[i]=b[i];for(;i<n;i++)a[i]=0;return d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'apply.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_dashboard_apply_layout_pb',str(D/'dashboard_apply_layout.c'),str(D/'dashboard_apply_literals.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,msg,ready=1,set_ret=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x400000)
  for addr,data in seg:u.mem_write(addr,data)
  ready_addr=sy['audio_uart_dashboard_ready'] if is_c else 0x20074fa5
  msg_addr=sy['audio_uart_dashboard_decoded'] if is_c else 0x2037cc68
  u.mem_write(ready_addr,bytes([ready]));u.mem_write(msg_addr,msg)
  set_addr=(sy['audio_dashboard_layout_set']&~1) if is_c else 0x558376
  flags_addr=(sy['audio_log_flags']&~1) if is_c else 0x43d0ce
  events=[]
  def hook(uc,addr,size,user):
   if addr==set_addr:
    p=uc.reg_read(UC_ARM_REG_R0)
    events.append(None if not p else bytes(uc.mem_read(p,128)))
    uc.reg_write(UC_ARM_REG_R0,set_ret)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif addr==flags_addr:
    uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_dashboard_apply_layout_pb'] if is_c else 0x502174)|1,0x600000,count=100000)
  return u.reg_read(UC_ARM_REG_R0),events
 def msg(pos=0,count=0,widgets=(),has=1,face=1):
  x=bytearray(188);x[0x30]=pos;x[0x34]=count;x[0x38]=len(widgets)
  x[0x3a:0x3a+len(widgets)]=bytes(widgets);x[0x3f]=has
  struct.pack_into('<H',x,0x40,face);x[0x44]=2;x[0x48]=1;x[0x49]=3
  return bytes(x)
 cases=[('not-ready',msg(),0,0),('base0',msg(),1,0),('base1',msg(1,2,(1,2)),1,0),
        ('base2',msg(2,5,(0,1,2,3,4)),1,0),('bad-base',msg(3),1,0),
        ('bad-widget',msg(0,1,(5,)),1,0),('no-face',msg(has=0),1,0),
        ('bad-face',msg(face=5),1,0),('set-fail',msg(),1,-1)]
 for face in (2,3,4):
  p=bytearray(msg(face=face));p[0x4c]=2;p[0x50]=2;p[0x52:0x54]=b'\x05\x06'
  p[0xae]=2;p[0xb0:0xb8]=b'\x11\x00\x00\x00\x22\x00\x00\x00'
  if face==4:p[0x4e:0x52]=b'abcd';p[0x6e:0x72]=b'efgh'
  cases.append((f'face{face}',bytes(p),1,0))
 for name,p,ready,ret in cases:
  a=run(False,p,ready,ret);b=run(True,p,ready,ret)
  assert a==b,(name,a,b)
 print('PASS_DASHBOARD_APPLY_NATIVE',len(cases))
