#!/usr/bin/env python3
"""Native/C radio file mode and seek/tell helper behavior."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_file_helpers.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
int32_t audio_file_tell(void *x){(void)x;return 0;}
int32_t audio_file_seek(void *x,int32_t y,uint32_t z){(void)x;(void)y;(void)z;return 0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_file_mode_52f3a0',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for flags in (0,1,2,3,0x100,0x101,0x400,0x401,0x500,0x501,0x800,0x801,0xfff):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,flags)
   u.emu_start((sym['audio_ble_radio_file_mode_52f3a0'] if is_c else 0x52f3a0)|1,0x600000,count=250)
   address=u.reg_read(UC_ARM_REG_R0);pair.append(bytes(u.mem_read(address,3)).split(b'\0',1)[0])
  assert pair[0]==pair[1],(flags,pair);count+=1
 for turns in ((0,0,123,0),(7,0,123,0),(7,-1,0,0),(7,0,123,1),(7,0,-1,0)):
  file,first,second,seek_error=turns;pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,file)
   tell=(sym['audio_file_tell']&~1) if is_c else 0x474870
   seek=(sym['audio_file_seek']&~1) if is_c else 0x474814
   calls=[];tells=[]
   def hook(uc,a,size,_):
    if a==tell:calls.append(('tell',uc.reg_read(UC_ARM_REG_R0)));ret=(first if not tells else second);tells.append(True)
    elif a==seek:
     calls.append(('seek',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
     ret=seek_error if len([x for x in calls if x[0]=='seek'])==1 else 0
    else:return
    uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_file_size_52f3f8'] if is_c else 0x52f3f8)|1,0x600000,count=300)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(turns,pair);count+=1
 print('PASS_RADIO_FILE_HELPERS_NATIVE',count)
