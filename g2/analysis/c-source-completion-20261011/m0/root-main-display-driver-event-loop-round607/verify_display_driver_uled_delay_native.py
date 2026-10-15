#!/usr/bin/env python3
"""Native/C VFP timing and ROM-call oracle for Apollo 0x4807a0."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
void display_driver_uled_rom_delay_00000040(uint32_t ticks){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=ticks;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'delay.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16',
                 '-mfloat-abi=hard','-mthumb','-std=c11','-ffreestanding',
                 '-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',
                 str(here/'display_driver_uled_delay.c'),str(d/'stub.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_delay_4807a0')
 cases=0
 for duration in (0,1,2,10,100,1000,0x10000,0x100000,0xffffff,
                  0x1000000,0x1000001,0x7fffffff,0xffffffff):
  for clock_mode in (0,0x10,0x18,0xffffffff):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0,0x1000)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    u.mem_map(0x40020000,0x10000)
    u.mem_map(0xe000e000,0x1000)
    for base,data in segments:u.mem_write(base,data)
    set32(u,0xe000ed88,0x00f00000)
    set32(u,0x40021000,clock_mode)
    reads=[]
    def on_read(_u,access,where,size,value,_user):
     if where==0x40021000:reads.append((where,size))
    u.hook_add(UC_HOOK_MEM_READ,on_read)
    def on_rom(_u,where,size,_user):
     if compiled or where!=0x40:return
     set32(u,0x20090000,get32(u,0x20090000)+1)
     set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,on_rom,begin=0x40,end=0x40)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,duration)
    u.emu_start((sym if compiled else 0x4807a0)|1,0x600000,count=3000)
    observed.append((bytes(u.mem_read(0x20090000,8)),reads))
   assert observed[0]==observed[1],(duration,clock_mode,observed)
   cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_DELAY_NATIVE',cases)
