#!/usr/bin/env python3
"""Native/C record byte updates and lower-call order for pair reset helpers."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_record_clear.c'
stub='''
#include <stdint.h>
__attribute__((naked)) uint32_t audio_ble_privacy_rewrite_record(uint8_t *p){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t audio_ble_pair_record_validate(uint8_t *p){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_record_clear_b',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  for name,native in [('audio_ble_pair_record_clear_a',0x47b488),
                      ('audio_ble_pair_record_clear_b',0x47b3cc)]:
    for value in (0,1,0xff):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        u.mem_write(0x20010000,b'\x72'*0xc8)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,0x20010000);u.reg_write(UC_ARM_REG_R1,value)
        seen=[]
        def hook(uc,a,size,_):
          if a in (0x479b74,sym['audio_ble_privacy_rewrite_record']&~1):
            seen.append(('rewrite',uc.reg_read(UC_ARM_REG_R0)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
          elif a in (0x47b730,sym['audio_ble_pair_record_validate']&~1):
            seen.append(('validate',uc.reg_read(UC_ARM_REG_R0)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((sym[name] if is_c else native)|1,0x600000,count=100)
        pair.append((seen,bytes(u.mem_read(0x20010080,0x48))))
      assert pair[0]==pair[1],(name,value,pair)
      cases+=1
  print('PASS_BLE_PAIR_RECORD_CLEAR_NATIVE',cases)
