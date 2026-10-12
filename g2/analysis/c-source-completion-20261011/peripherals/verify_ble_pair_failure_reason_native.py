#!/usr/bin/env python3
"""Native/C 256-status pairing reason and status-five privacy cleanup."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_failure_reason.c'
stub='''
#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[256];
__attribute__((naked)) void audio_ble_privacy_reset_local(void){__asm volatile("bx lr");}
__attribute__((naked)) void DmPrivClearResList(void){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_failure_reason',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  for code in range(256):
    pair=[]
    for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for a,d in seg:u.mem_write(a,d)
      base=sym['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
      u.mem_write(base+0x6c,b'\x11')
      u.mem_write(base+0x70,b'\x12\x34\x56\x78')
      u.mem_write(base+0x74,b'\x22')
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,code)
      seen=[]
      def hook(uc,a,size,_):
        if a in (0x47acf8,sym['audio_ble_privacy_reset_local']&~1):
          seen.append('local');uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x4d28b0,sym['DmPrivClearResList']&~1):
          seen.append('controller');uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,hook)
      u.emu_start((sym['audio_ble_pair_failure_reason'] if is_c else 0x4b8390)|1,0x600000,count=220)
      pointer=u.reg_read(UC_ARM_REG_R0)
      text=bytes(u.mem_read(pointer,100)).split(b'\0')[0]
      pair.append((text,seen,bytes(u.mem_read(base+0x6c,9))))
    assert pair[0]==pair[1],(code,pair)
    cases+=1
  print('PASS_BLE_PAIR_FAILURE_REASON_NATIVE',cases)
