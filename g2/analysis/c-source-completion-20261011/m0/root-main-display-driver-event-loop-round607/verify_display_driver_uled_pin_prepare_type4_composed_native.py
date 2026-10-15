#!/usr/bin/env python3
"""Composed native/C oracle for Apollo type-4 prepare, finalize and wait."""
from itertools import product
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
static void log_call(uint32_t id,uint32_t a,uint32_t b,uint32_t c){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;uint32_t n=p[0];
p[1+n*4]=id;p[2+n*4]=a;p[3+n*4]=b;p[4+n*4]=c;p[0]=n+1;}
uint32_t display_driver_uled_pin_query_4c37a8(uint32_t a,uint32_t b){
log_call(1,a,b,0);return *(volatile uint32_t*)0x20090100;}
uint32_t display_driver_uled_pin_group_check_4c37ca(uint32_t a){
log_call(2,a,0,0);return *(volatile uint32_t*)0x20090104;}
uint32_t display_driver_uled_power_set_4d391e(uint32_t a){log_call(3,a,0,0);return 0;}
uint32_t display_driver_uled_power_apply_4d3938(uint32_t a){
log_call(4,a,0,0);return *(volatile uint32_t*)0x20090108;}
uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t a,uint32_t b,uint32_t c){
log_call(5,a,b,c);return 0;}
void display_driver_uled_delay_4807a0(uint32_t ms){
log_call(6,ms,0,0);*(volatile uint8_t*)0x20074f57=0;}
'''
targets={0x4c37a8:1,0x4c37ca:2,0x4d391e:3,0x4d3938:4,0x4c37fe:5,0x4807a0:6}
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'prepare4.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_prepare_type4.c'),
                 str(here/'display_driver_uled_pin_prepare_finalize.c'),
                 str(here/'display_driver_uled_irq_save.c'),str(d/'stubs.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_prepare_type4_4c3f2a')
 cases=0
 for pin,query,flag,disabled,group,enabled,apply_status,flag59,prior in product(
    (0x10,0x138),(0,1),(0,1),(0,1),(0,1),(0,1),(0,5),(0,1),(0,1)):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   for base,data in segments:u.mem_write(base,data)
   set32(u,0x20090100,query);set32(u,0x20090104,group)
   set32(u,0x20090108,apply_status)
   u.mem_write(0x20074f57,bytes([flag]))
   u.mem_write(0x20004536,bytes([disabled]))
   u.mem_write(0x20074f59,bytes([flag59]))
   set32(u,0x20074250,enabled)
   set32(u,0x20073f30,0x12345678)
   set32(u,0x20074264,0x20088000 if flag else 0)
   set32(u,0x20088000,0xface1234)
   def on_call(_u,address,size,_user):
    if compiled or address not in targets:return
    id=targets[address]
    a=u.reg_read(UC_ARM_REG_R0)
    b=u.reg_read(UC_ARM_REG_R1) if id in (1,5) else 0
    c=u.reg_read(UC_ARM_REG_R2) if id==5 else 0
    n=get32(u,0x20090000)
    for j,value in enumerate((id,a,b,c)):set32(u,0x20090004+(n*4+j)*4,value)
    set32(u,0x20090000,n+1)
    if id==6:u.mem_write(0x20074f57,b'\x00')
    ret=query if id==1 else group if id==2 else apply_status if id==4 else 0
    u.reg_write(UC_ARM_REG_R0,ret)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,on_call,begin=min(targets),end=max(targets))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
   u.emu_start((sym if compiled else 0x4c3f2a)|1,0x600000,count=5000)
   cell=get32(u,0x20074264)
   observations.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
     bytes(u.mem_read(0x20074f57,3)),bool(cell),bytes(u.mem_read(0x20090000,256))))
  assert observations[0]==observations[1],(
   pin,query,flag,disabled,group,enabled,apply_status,flag59,prior,observations)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_PREPARE_TYPE4_COMPOSED_NATIVE',cases)
