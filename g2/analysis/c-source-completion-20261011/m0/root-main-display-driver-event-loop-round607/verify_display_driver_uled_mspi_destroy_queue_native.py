#!/usr/bin/env python3
"""Native/C queue-edge discriminator for Apollo MSPI destroy 0x4c240e.

Direct callees are replaced by identical controlled stubs on both sides.
This proves only the selected caller paths and their observable effects.
"""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP

here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
static void log_call(uint32_t id){volatile uint32_t *p=(volatile uint32_t*)0x20090000;
uint32_t n=p[0];p[n+1]=id;p[0]=n+1;}
uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t q,uint32_t*s){
(void)q;log_call(1);s[0]=*(uint32_t*)(s[0]+0x1c);s[3]=0;
return *(volatile uint32_t*)0x20090100;}
uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t q){(void)q;log_call(2);return 0;}
uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t*h){(void)h;log_call(3);return 0;}
uint32_t display_driver_uled_mspi_dma_stop_4bfd62(uint32_t*h){(void)h;log_call(4);return 0;}
uint32_t display_driver_uled_mspi_dma_next_4bfdf4(uint32_t*h){(void)h;log_call(5);return 0;}
uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t a,uint32_t b){
(void)a;(void)b;log_call(6);return 0;}
'''
addresses={0x53901a:1,0x5390fc:2,0x4bfd44:3,0x4bfd62:4,
           0x4bfdf4:5,0x4c4530:6}
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'destroy.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_destroy.c'),
                 str(d/'stubs.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_child_4c240e')
 cases=0
 for kind in ('snapshot_error','snapshot_success','fatal_one','fatal_two'):
  for instance in (0,1,3):
   for callback in (False,True):
    if kind.startswith('snapshot') and callback:continue
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     u.mem_map(0x40060000,0x10000)
     for base,data in segments:u.mem_write(base,data)
     h=0x20080000;set32(u,h,0x01bebebe);set32(u,h+4,instance)
     set32(u,h+0x20,2 if kind=='fatal_two' else 1)
     u.mem_write(h+0x8c9,b'\x04')
     if callback:set32(u,h+0x28+4,0x120001);set32(u,h+0x428+4,0x12345678)
     set32(u,0x20052c00+instance*0x8d0,0x20072000)
     set32(u,0x20090100,5 if kind=='snapshot_error' else 0)
     base=0x40060000+(instance<<12)
     set32(u,base+0x100,0xfeed4321);set32(u,base+0x30,0x12345678)
     set32(u,base+0x2ac,0xabcdef00)
     flags=0x1880 if kind.startswith('fatal') else 0x40
     writes=[]
     def on_write(_u,access,address,size,value,_user):
      if access==UC_HOOK_MEM_WRITE and 0x40060000<=address<0x40070000:
       writes.append((address,size,value))
     u.hook_add(UC_HOOK_MEM_WRITE,on_write)
     def on_call(_u,address,size,_user):
      if address==0x120000:
       n=get32(u,0x20090000);set32(u,0x20090004+n*4,7);set32(u,0x20090000,n+1)
       u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
      if compiled or address not in addresses:return
      id=addresses[address];n=get32(u,0x20090000)
      set32(u,0x20090004+n*4,id);set32(u,0x20090000,n+1)
      if id==1:
       snap=u.reg_read(UC_ARM_REG_R1)
       set32(u,snap,get32(u,h+0x1c));set32(u,snap+12,0)
       ret=get32(u,0x20090100)
      else:ret=0
      u.reg_write(UC_ARM_REG_R0,ret)
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,on_call,begin=min(*addresses,0x120000),end=max(addresses))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,h);u.reg_write(UC_ARM_REG_R1,flags)
     u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0)
     u.emu_start((sym if compiled else 0x4c240e)|1,0x600000,count=50000)
     observations.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(h,0x8d0)),
       bytes(u.mem_read(base,0x2b8)),bytes(u.mem_read(0x20090000,32)),writes))
    assert observations[0]==observations[1],(kind,instance,callback,
      observations[0][0],observations[1][0],observations[0][3],observations[1][3],
      observations[0][4],observations[1][4])
    cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_DESTROY_QUEUE_NATIVE',cases)
