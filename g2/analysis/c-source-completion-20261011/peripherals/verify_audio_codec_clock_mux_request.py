#!/usr/bin/env python3
"""Original-byte/C clock mux request with deterministic child contracts."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_clock_mux_request_source_candidate/request.c';O=D/'codec-mux-request-m4.o';L=D/'codec-mux-lowers-m4.o';E=D/'codec-mux-request-oracle.elf';stub=D/'codec-mux-lowers.c'
stub.write_text('''#include <stdint.h>\n#define F(n,t) __attribute__((noinline)) uint8_t n(uint8_t x){return (uint8_t)(x+t);}\nF(g2_clock_mux_group,0) F(g2_clock_mux_setting,0) F(g2_clock_mux_mask,0) F(g2_clock_mux_path,0)\n__attribute__((noinline)) void g2_clock_mux_prepare(uint8_t g,uint8_t*p){*p=g;}\n__attribute__((noinline)) void g2_clock_mux_gate(uint8_t p,uint8_t m){(void)p;(void)m;}\n__attribute__((noinline)) void stock_delay_us(uint32_t x){(void)x;}\n''')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
orig={'group':0x539348,'setting':0x539352,'prepare':0x539c9a,'mask':0x539372,'path':0x53935c,'gate':0x44b0d6,'delay':0x4807a0}
name={'group':'g2_clock_mux_group','setting':'g2_clock_mux_setting','prepare':'g2_clock_mux_prepare','mask':'g2_clock_mux_mask','path':'g2_clock_mux_path','gate':'g2_clock_mux_gate','delay':'stock_delay_us'}
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def run(original,source,delay,control):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000);u.mem_map(0x47ff0000,0x1000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 put(u,0x400204e8,control);u.reg_write(A.UC_ARM_REG_R0,source);u.reg_write(A.UC_ARM_REG_R1,delay);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 hooks={v:k for k,v in (orig if original else {k:sym[name[k]]&~1 for k in orig}).items()}
 calls=[];writes=[];done=[False]
 def code(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop();return
  if pc not in hooks:return
  k=hooks[pc];r0=c.reg_read(A.UC_ARM_REG_R0);r1=c.reg_read(A.UC_ARM_REG_R1)
  calls.append((k,r0,r1) if k=='gate' else (k,r0))
  if k=='group':ret=r0%6
  elif k=='setting':ret=r0%4
  elif k=='prepare':c.mem_write(r1,bytes([r0%5]));ret=0
  elif k=='mask':ret=1<<(r0&3)
  elif k=='path':ret=r0+1
  else:ret=0
  c.reg_write(A.UC_ARM_REG_R0,ret);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 def write(_c,_a,a,size,v,_):
  if a==0x400204e8:writes.append((a,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x539bbc if original else sym['g2_codec_clock_mux_request'])|1,0,count=500)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),calls,writes,get(u,0x400204e8)
n=0
for source in range(12):
 for delay in (0,17,200):
  for control in (0,0xffffffff,0x12345678):
   a=run(True,source,delay,control);b=run(False,source,delay,control)
   assert a==b,(source,delay,control,a,b)
   n+=1
print('PASS_AUDIO_CODEC_CLOCK_MUX_REQUEST',n)
for p in (O,L,E,stub):p.unlink()
