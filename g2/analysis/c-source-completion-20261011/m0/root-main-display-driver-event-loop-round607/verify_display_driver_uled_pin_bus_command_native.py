#!/usr/bin/env python3
"""Native/C command, return and MMIO-order oracle for Apollo 0x4809c4."""
from itertools import product
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
static uint32_t call(uint32_t id,uint32_t a,uint32_t b){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;uint32_t n=p[0];
p[1+n*3]=id;p[2+n*3]=a;p[3+n*3]=b;p[0]=n+1;
return id==1?0:*(volatile uint32_t*)0x20090100;}
void display_driver_uled_delay_4807a0(uint32_t x){(void)call(1,x,0);}
uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t a,uint32_t b){return call(2,a,b);}
uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t a,uint32_t b){return call(3,a,b);}
'''
targets={0x4807a0:1,0x4c44bc:2,0x4c4530:3}
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'bus.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_bus_command.c'),
                 str(d/'stubs.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_bus_command_4809c4')
 cases=0
 for command,option,provider_result,initial in product(
    range(8),(None,0,1,2,3,7,8),(0,5),(0,0x12345678,0xffffffff)):
  observed=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   u.mem_map(0x40020000,0x10000)
   for base,data in segments:u.mem_write(base,data)
   for a in (0x40020120,0x40020128,0x4002012c):set32(u,a,initial)
   u.mem_write(0x200001e0,b'\x2d');set32(u,0x200001e4,0xabc)
   set32(u,0x20088000,0 if option is None else option)
   set32(u,0x20090100,provider_result)
   accesses=[]
   def on_mmio(_u,kind,where,size,value,_user):
    if where in (0x40020120,0x40020128,0x4002012c):
     accesses.append((kind,where,size,value if kind==UC_HOOK_MEM_WRITE else None))
   u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,on_mmio)
   def on_callee(_u,where,size,_user):
    if compiled or where not in targets:return
    id=targets[where];n=get32(u,0x20090000)
    for j,v in enumerate((id,u.reg_read(UC_ARM_REG_R0),
                           u.reg_read(UC_ARM_REG_R1) if id!=1 else 0)):
     set32(u,0x20090004+(n*3+j)*4,v)
    set32(u,0x20090000,n+1)
    u.reg_write(UC_ARM_REG_R0,0 if id==1 else provider_result)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,on_callee,begin=min(targets),end=max(targets))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,command)
   u.reg_write(UC_ARM_REG_R1,0 if option is None else 0x20088000)
   u.emu_start((sym if compiled else 0x4809c4)|1,0x600000,count=6000)
   observed.append((u.reg_read(UC_ARM_REG_R0),
       bytes(u.mem_read(0x40020120,4)),bytes(u.mem_read(0x40020128,4)),
       bytes(u.mem_read(0x4002012c,4)),bytes(u.mem_read(0x20090000,100)),
       accesses))
  assert observed[0]==observed[1],(command,option,provider_result,initial,observed)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_BUS_COMMAND_NATIVE',cases)
