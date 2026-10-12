#!/usr/bin/env python3
"""Actual native/C successful GPU mode change with callback slot empty."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];D=R/'components/audio/power_vendor_candidate'
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
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
 for mode,current in ((3,0),(0,3)):
  for regseed in (0,0xffffffff,0x12345678):
   for callback_return in (None,0,7):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
     u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
     for a,d in segments:u.mem_write(a,d)
     u.mem_write(0x40021108,(0x30).to_bytes(4,'little'))
     u.mem_write(0x40021008,(0).to_bytes(4,'little'))
     u.mem_write(0x40021090,regseed.to_bytes(4,'little'))
     u.mem_write(0x4002108c,regseed.to_bytes(4,'little'))
     u.mem_write(0x20074f60,bytes([current,current]))
     u.mem_write(0x20073294,(0 if callback_return is None else 0x100801).to_bytes(4,'little'))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,mode)
     events=[]
     saves=(sym['g2_power_critical_save']&~1) if is_c else 0x473940
     delays=(sym['audio_delay_us']&~1) if is_c else 0x4807a0
     def hook(uc,a,size,_):
      if a==saves:events.append(('save',));ret=0
      elif a==delays:events.append(('delay',uc.reg_read(UC_ARM_REG_R0)));ret=0
      elif a==0x100800:events.append(('callback',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));ret=callback_return
      else:return
      uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     writes=[]
     def written(uc,access,a,size,value,_):
      if a in (0x40021090,0x4002108c,0x20074f60,0x20074f61):writes.append((a,size,value))
     u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
     u.emu_start((sym['g2_power_gpu_mode_select'] if is_c else 0x47f11c)|1,0x600000,count=5000)
     pair.append((u.reg_read(UC_ARM_REG_R0),events,writes,bytes(u.mem_read(0x20074f60,2))))
    assert pair[0]==pair[1],(mode,current,regseed,callback_return,pair)
    count+=1
 print('PASS_POWER_GPU_TRANSITION_EFFECTS',count)
