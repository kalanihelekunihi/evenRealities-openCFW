#!/usr/bin/env python3
"""Bounded nonfloating stock/C oracle for complete I2S configuration body."""
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_configure_source_candidate/configure.c';O=D/'codec-i2s-configure-m4.o';L=D/'codec-i2s-configure-lowers-m4.o';E=D/'codec-i2s-configure-oracle.elf';stub=D/'codec-i2s-configure-lowers.c'
stub.write_text('''#include <stdint.h>\n__attribute__((noinline)) void stock_delay_us(uint32_t x){(void)x;}\n__attribute__((noinline)) uint32_t audio_i2s_clock_source(uint32_t x){return x;}\n__attribute__((noinline)) uint64_t __aeabi_d2ulz(double x){return (uint64_t)x;}\n''')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=softfp','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_codec_chip_revision=0x4002000c','-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,valid,started,instance,config_mode,frame_mode,source_enabled,source=0x100,frequency=4.25):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40208000,0x3000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 h=0x20002000;c=0x20003000;slots=0x20004000;frame=0x20005000;base=0x40208000+instance*0x1000
 put(u,h,(0x01125125 if valid else 0xdeadbeef)|(0x02000000 if started else 0));put(u,h+4,instance)
 put(u,c+0x1c,slots);put(u,c+0x20,frame);put(u,c+4,source);put(u,c+8,1 if source_enabled else 0);put(u,c+0x18,1 if source_enabled else 0)
 u.mem_write(c+0x10,struct.pack('<d',frequency))
 u.mem_write(c,bytes([config_mode,1]));u.mem_write(slots,bytes([0]));put(u,slots+4,2);put(u,slots+8,0)
 u.mem_write(slots+0xc,bytes([2,0]));u.mem_write(slots+0x14,bytes([0,0,0]));u.mem_write(frame,bytes([frame_mode]));put(u,frame+4,5)
 u.mem_write(frame+8,bytes([0,0,0]));put(u,base+0x54,0x1234);put(u,base+0x100,0x98765432);put(u,0x4002000c,0)
 u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,c);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 lower={0x4807a0:'delay',0x58fd1c:'clock',0x59823c:'convert'} if original else {sym['stock_delay_us']&~1:'delay',sym['audio_i2s_clock_source']&~1:'clock',sym['__aeabi_d2ulz']&~1:'convert'}
 calls=[];writes=[];done=[False]
 def hook(cpu,pc,_s,_):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
  elif pc in lower:
   n=lower[pc];v=cpu.reg_read(A.UC_ARM_REG_R0)
   if n=='convert':
    value=struct.unpack('<d',struct.pack('<II',v,cpu.reg_read(A.UC_ARM_REG_R1)))[0]
    result=int(value)&0xffffffffffffffff
    calls.append((n,round(value,8)))
    cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_R1,result>>32)
   else:
    calls.append((n,v));cpu.reg_write(A.UC_ARM_REG_R0,4 if n=='clock' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 def write(_cpu,_a,a,size,v,_):
  if 0x40208000<=a<0x4020b000 or h<=a<h+0x100:writes.append((a,size,v&((1<<(size*8))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x590104 if original else sym['g2_codec_i2s_configure'])|1,0,count=1500)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),calls,writes,bytes(u.mem_read(h,100)),bytes(u.mem_read(base,0x110))
n=0
for valid in (False,True):
 for started in (False,True):
  for instance in (0,1):
   for config_mode in (0,1,2):
    for frame_mode in (0,1,2,3):
     for source_enabled in (False,True):
      a=run(True,valid,started,instance,config_mode,frame_mode,source_enabled);b=run(False,valid,started,instance,config_mode,frame_mode,source_enabled)
      assert a==b,(valid,started,instance,config_mode,frame_mode,source_enabled,a[:3],b[:3])
      n+=1
print('PASS_AUDIO_CODEC_I2S_CONFIGURE_NONFLOAT',n)
# The native double-precision path executes VFP instructions not supported by
# this Cortex-M4 Unicorn model; it remains a static source correspondence.
for p in (O,L,E,stub):p.unlink()
