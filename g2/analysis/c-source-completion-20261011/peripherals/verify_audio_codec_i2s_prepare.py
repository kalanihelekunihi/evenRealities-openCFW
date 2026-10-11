#!/usr/bin/env python3
"""Bounded original-byte/C oracle for I2S prepare with controlled clock children."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_i2s_prepare_source_candidate/prepare.c'
O = D / 'codec-i2s-prepare-m4.o'
L = D / 'codec-i2s-prepare-lowers-m4.o'
E = D / 'codec-i2s-prepare-oracle.elf'
lowers = D / 'codec-i2s-prepare-lowers.c'
lowers.write_text('''#include <stdint.h>\n__attribute__((noinline)) uint32_t audio_power_clock_acquire(uint32_t a,uint32_t b){return a+b;}\n__attribute__((noinline)) uint32_t audio_power_clock_release(uint32_t a,uint32_t b){return a+b;}\n__attribute__((noinline)) uint32_t audio_i2s_clock_source(uint32_t a){return a;}\n__attribute__((noinline)) void audio_power_reconfigure(uint32_t a,uint32_t b){(void)a;(void)b;}\n''')
for source, obj in ((S,O),(lowers,L)):
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O),str(L)],check=True)
with E.open('rb') as fh:
    elf=ELFFile(fh)
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
names=['audio_power_clock_acquire','audio_power_clock_release','audio_i2s_clock_source','audio_power_reconfigure']
orig=[0x4c44bc,0x4c4530,0x58fd1c,0x58fdbc]

def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def run(original,valid,started,source_on,clock_result,channel):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000)
    u.mem_map(0x20000000,0x100000);u.mem_map(0x40208000,0x3000)
    if original:u.mem_write(0x438000,stock)
    else:
        for a,b in segments:u.mem_write(a,b)
    h=0x20002000;reg=0x40208000+channel*0x1000+0x100
    put(u,h,(0x01125125 if valid else 0xdeadbeef)|(0x02000000 if started else 0));put(u,h+4,channel)
    put(u,h+0x5c,0x203);u.mem_write(h+0x60,bytes([source_on]));put(u,reg,0x55aa55aa)
    u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
    events=[];writes=[];done=[False]
    hooks=dict(zip(orig if original else [sym[n]&~1 for n in names],names))
    def code(cpu,pc,_sz,_):
        if pc==0x101180:done[0]=True;cpu.emu_stop();return
        if pc in hooks:
            n=hooks[pc];a=cpu.reg_read(A.UC_ARM_REG_R0);b=cpu.reg_read(A.UC_ARM_REG_R1)
            events.append((n,a,b) if n != 'audio_i2s_clock_source' else (n,a))
            result=(clock_result if n=='audio_power_clock_acquire' and (a==4 or clock_result==2) else 0)
            if n=='audio_i2s_clock_source':result=5
            cpu.reg_write(A.UC_ARM_REG_R0,result);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    def write(_cpu,_access,a,size,value,_):
        if h<=a<h+0x100 or 0x40208000<=a<0x4020b000:writes.append((a,size,value&((1<<(8*size))-1)))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start((0x590b92 if original else sym['g2_codec_i2s_prepare'])|1,0,count=500)
    assert done[0]
    return u.reg_read(A.UC_ARM_REG_R0),events,writes,get(u,h),get(u,reg)

cases=0
for valid in (False,True):
 for started in (False,True):
  for source_on in (0,1):
   for clock_result in (0,2):
    for channel in (0,1):
     a=run(True,valid,started,source_on,clock_result,channel)
     b=run(False,valid,started,source_on,clock_result,channel)
     assert a==b,(valid,started,source_on,clock_result,channel,a,b)
     cases+=1
print('PASS_AUDIO_CODEC_I2S_PREPARE',cases)
for p in (O,L,E,lowers):p.unlink()
