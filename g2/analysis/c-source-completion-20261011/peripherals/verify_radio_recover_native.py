#!/usr/bin/env python3
"""Stock/C firmware image init gate and log effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_recover.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_ble_radio_image_load_52f442(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_recover_52fb58',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for active,result in ((1,0),(0,0),(0,1)):
  for flags in (0,2):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20075016,bytes([active]));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    maps={0x52f442:'load',0x43d0ce:'flags',0x43d574:'extended'} if not is_c else {sym[n]&~1:k for n,k in [('audio_ble_radio_image_load_52f442','load'),('audio_log_flags','flags'),('audio_log_extended','extended')]}
    events=[]
    def hook(uc,a,size,_):
     kind=maps.get(a)
     if kind is None:return
     if kind=='load':events.append((kind,));ret=result
     elif kind=='flags':events.append((kind,));ret=flags
     else:
      sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');fmt=int.from_bytes(uc.mem_read(sp+4,4),'little')
      events.append((kind,uc.reg_read(UC_ARM_REG_R0),line,bytes(uc.mem_read(fmt,64)).split(b'\0',1)[0]));ret=0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_hci_radio_recover_52fb58'] if is_c else 0x52fb58)|1,0x600000,count=700)
    pair.append((events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20075016,1))))
   assert pair[0]==pair[1],(active,result,flags,pair)
   count+=1
 print('PASS_RADIO_RECOVER_NATIVE',count)
