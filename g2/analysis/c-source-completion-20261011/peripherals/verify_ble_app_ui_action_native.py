#!/usr/bin/env python3
"""Native/C AppUiAction callback and compressed diagnostic for all byte actions."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_ui_action.c'
stub='''
#include <stdint.h>
uintptr_t audio_ble_ui_callback_cells[2];
__attribute__((noinline)) uint32_t audio_log_flags(void){asm volatile("");return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){asm volatile(""::"r"(a),"r"(b),"r"(c),"r"(d),"r"(e),"r"(f));}
__attribute__((noinline)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){asm volatile(""::"r"(a),"r"(b),"r"(c));return 0;}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_event_state',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  for event in list(range(32))+[0xff]:
    for flags in (0,1,2):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        u.mem_write(0x20073f64,struct.pack('<I',0x500001))
        if is_c:u.mem_write(sym['audio_ble_ui_callback_cells']+4,struct.pack('<I',0x500001))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,event)
        seen=[]
        def string(uc,p):
          return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode(errors='replace')
        def hook(uc,a,size,_):
          if a in (0x43d0ce,sym['audio_log_flags']&~1):
            uc.reg_write(UC_ARM_REG_R0,flags)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
          elif a in (0x43ce9e,sym['compressed_log_output']&~1):
            seen.append(('log',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
          elif a in (0x43d574,sym['audio_log_extended']&~1):
            sp=uc.reg_read(UC_ARM_REG_SP)
            line,msg=struct.unpack('<II',bytes(uc.mem_read(sp,8)))
            seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,msg)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
          elif a==0x500000:
            seen.append(('callback',uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((sym['audio_ble_slave_event_state'] if is_c else 0x4bd054)|1,0x600000,count=550)
        pair.append(seen)
      assert pair[0]==pair[1],(event,flags,pair)
      cases+=1
  print('PASS_BLE_APP_UI_ACTION_NATIVE',cases)
