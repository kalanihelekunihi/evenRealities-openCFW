#!/usr/bin/env python3
"""Native/C controlled-callee oracle for Apollo type-4 pin control 0x4c4016."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
static uint32_t call(uint32_t id,uint32_t a,uint32_t b,uint32_t c){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;uint32_t n=p[0];
p[1+n*4]=id;p[2+n*4]=a;p[3+n*4]=b;p[4+n*4]=c;p[0]=n+1;
return id==1?*(volatile uint32_t*)0x20090100:
       id==3?*(volatile uint32_t*)0x20090104:0;}
uint32_t display_driver_uled_pin_query_4c37a8(uint32_t a,uint32_t b){return call(1,a,b,0);}
uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t a,uint32_t b,uint32_t c){return call(2,a,b,c);}
uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t a){return call(3,a,0,0);}
uint32_t display_driver_uled_power_set_4d391e(uint32_t a){return call(4,a,0,0);}
'''
targets={0x4c37a8:1,0x4c37fe:2,0x4c377a:3,0x4d391e:4}
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'control4.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_control_type4.c'),
                 str(here/'display_driver_uled_irq_save.c'),str(d/'stubs.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_control_type4_4c4016')
 cases=0
 for pin in (0,0x10,0x38,0x100,0x138):
  for query in (0,1,6):
   for group in (0,1):
    for prior in (0,1):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      set32(u,0x20090100,query);set32(u,0x20090104,group)
      def on_call(_u,address,size,_user):
       if compiled or address not in targets:return
       id=targets[address];n=get32(u,0x20090000)
       args=(u.reg_read(UC_ARM_REG_R0),
             u.reg_read(UC_ARM_REG_R1) if id in (1,2) else 0,
             u.reg_read(UC_ARM_REG_R2) if id==2 else 0)
       for j,value in enumerate((id,*args)):
        set32(u,0x20090004+(n*4+j)*4,value)
       set32(u,0x20090000,n+1)
       ret=query if id==1 else group if id==3 else 0
       u.reg_write(UC_ARM_REG_R0,ret)
       u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,on_call,begin=min(targets),end=max(targets))
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
      u.emu_start((sym if compiled else 0x4c4016)|1,0x600000,count=3000)
      observed.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
                       bytes(u.mem_read(0x20090000,96))))
     assert observed[0]==observed[1],(pin,query,group,prior,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_CONTROL_TYPE4_NATIVE',cases)
