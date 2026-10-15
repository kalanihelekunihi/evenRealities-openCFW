#!/usr/bin/env python3
"""Native/C dispatch and ABI oracle for Apollo pin prepare 0x4c44bc."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[0x4c3bfc,0x4c3c60,0x4c3d9e,0x4c3cd4,0x4c3f2a,0x4c4086,0x4c427e]
names=['display_driver_uled_pin_prepare_type0_4c3bfc',
       'display_driver_uled_pin_prepare_type1_4c3c60',
       'display_driver_uled_pin_prepare_type2_4c3d9e',
       'display_driver_uled_pin_prepare_type3_4c3cd4',
       'display_driver_uled_pin_prepare_type4_4c3f2a',
       'display_driver_uled_pin_prepare_type5_4c4086',
       'display_driver_uled_pin_prepare_type6_4c427e']
stub='#include <stdint.h>\n'
for i,name in enumerate(names):
 stub+=f'''uint32_t {name}(uint32_t x){{
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]={i+1}u;p[1]=x;
return 0x100u+{i+1}u;}}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'pin.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_pin_prepare.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_dma_pin_prepare_4c44bc')
 cases=0
 for kind in (0,1,2,3,4,5,6,7,0xff,0x100,0x104):
  for pin in (0,1,0x10,0x38,0x39,0xff,0x100,0x138):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    def on_callee(_u,address,size,_user):
     if compiled or address not in callees:return
     i=callees.index(address)+1
     set32(u,0x20090000,i);set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
     u.reg_write(UC_ARM_REG_R0,0x100+i)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,on_callee,begin=min(callees),end=max(callees))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,kind);u.reg_write(UC_ARM_REG_R1,pin)
    u.emu_start((sym if compiled else 0x4c44bc)|1,0x600000,count=1000)
    observed.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20090000,8))))
   assert observed[0]==observed[1],(kind,pin,observed)
   cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_PIN_PREPARE_NATIVE',cases)
