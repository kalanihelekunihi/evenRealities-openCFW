#!/usr/bin/env python3
"""Native/C WSF OS signal task and ISR paths with child notification cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_os_signal.c'
stub='''#include <stdint.h>
void *audio_wsf_event_group;
__attribute__((naked)) uint32_t g2_log_is_privileged(void){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t g2_log_exception_number(void){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t xEventGroupSetBitsFromISR(void *h,uint32_t b,int32_t*w){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t xEventGroupSetBits(void *h,uint32_t b){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfSetOsSpecificEvent',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for handle in (0,0x2007f000):
  for isr in (0,1):
   for notified in (0,1):
    for woken in (0,1):
     pair=[]
     for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x1000)
      for a,d in seg:u.mem_write(a,d)
      cell=sym['audio_wsf_event_group'] if is_c else 0x20074ef0
      u.mem_write(cell,handle.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      seen=[]
      def hook(uc,a,size,_):
       if a==0x442228:uc.reg_write(UC_ARM_REG_R0,isr);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
       if a==(sym['g2_log_is_privileged']&~1):uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
       if a==(sym['g2_log_exception_number']&~1):uc.reg_write(UC_ARM_REG_R0,isr);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
       if a in (0x47ee4a,sym['xEventGroupSetBitsFromISR']&~1):
        seen.append(('isr',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.mem_write(uc.reg_read(UC_ARM_REG_R2),woken.to_bytes(4,'little'));uc.reg_write(UC_ARM_REG_R0,notified);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
       if a in (0x47ed76,sym['xEventGroupSetBits']&~1):seen.append(('task',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,notified);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      u.hook_add(UC_HOOK_CODE,hook)
      u.emu_start((sym['WsfSetOsSpecificEvent'] if is_c else 0x52b8d8)|1,0x600000,count=500)
      pair.append((seen,bytes(u.mem_read(0xe000ed04,4))))
     assert pair[0]==pair[1],(handle,isr,notified,woken,pair)
     cases+=1
 print('PASS_BLE_WSF_OS_SIGNAL_NATIVE',cases)
