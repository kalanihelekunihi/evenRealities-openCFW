#!/usr/bin/env python3
"""Actual native/C GPU transition guard and same-mode effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/power_vendor_candidate'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include "power.h"
uint32_t g2_power_critical_save(void){return 0;}
void g2_power_critical_restore(uint32_t a){(void)a;}
void audio_delay_us(uint32_t a){(void)a;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,g2_power_gpu_mode_select','-I'+str(D),str(D/'power_gpu_transition_native.c'),str(D/'power_descriptor_native.c'),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for mode in (0,1,2,3,0x103):
  for gpu_rate in (0,3):
   for status in (0,1):
    for current,previous in ((0,0),(0,3),(3,0),(3,3)):
     pair=[]
     for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
      for a,d in segments:u.mem_write(a,d)
      u.mem_write(0x40021108,(gpu_rate<<4).to_bytes(4,'little'))
      u.mem_write(0x40021008,(status*0x40000).to_bytes(4,'little'))
      u.mem_write(0x20074f60,bytes([current,previous]))
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,mode)
      reached=[];stop=(sym['g2_power_critical_save']&~1) if is_c else 0x473940
      def hook(uc,a,size,_):
       if a==stop:reached.append(True);uc.emu_stop()
      u.hook_add(UC_HOOK_CODE,hook)
      u.emu_start((sym['g2_power_gpu_mode_select'] if is_c else 0x47f11c)|1,0x600000,count=1000)
      pair.append((bool(reached),None if reached else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20074f60,2))))
     assert pair[0]==pair[1],(mode,gpu_rate,status,current,previous,pair)
     count+=1
 print('PASS_POWER_GPU_TRANSITION_GUARDS',count)
