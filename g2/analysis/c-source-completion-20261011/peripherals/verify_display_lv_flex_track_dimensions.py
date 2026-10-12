"""Actual ARM C/native flex min/max property and margin extents."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
BASE=ROOT/'components/audio/uart_thread_source_candidate'
SRC=BASE/'display_lv_flex_track_dimensions.c'
WRAP=BASE/'display_lv_flex_repos_selectors.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){return 0;}
int32_t audio_uart_lv_obj_width_43fd9e(void*a){return 0;}
int32_t audio_uart_lv_obj_height_43fdda(void*a){return 0;}
'''
CASES=[(0x48b914,'audio_uart_lv_flex_min_width_48b914'),
       (0x48b91e,'audio_uart_lv_flex_min_height_48b91e'),
       (0x48b932,'audio_uart_lv_flex_max_width_48b932'),
       (0x48b93c,'audio_uart_lv_flex_max_height_48b93c'),
       (0x48c7b4,'audio_uart_lv_flex_width_margin_48c7b4'),
       (0x48c7d8,'audio_uart_lv_flex_height_margin_48c7d8')]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text(SHIM);elf=Path(td)/'dims.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_flex_width_margin_48c7b4',
                 str(SRC),str(WRAP),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for native,name in CASES:
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,5)
   addresses={(syms[n]&~1 if is_c else addr):n for addr,n in ((0x44bdea,'audio_uart_lv_style_property_44bdea'),
       (0x43fd9e,'audio_uart_lv_obj_width_43fd9e'),(0x43fdda,'audio_uart_lv_obj_height_43fdda'))}
   calls=[]
   def hook(uc,a,size,_):
    if a not in addresses:return
    n=addresses[a];calls.append((n,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2) if n.endswith('44bdea') else None))
    uc.reg_write(UC_ARM_REG_R0,0x12345678 if n.endswith('44bdea') else 30 if n.endswith('43fd9e') else 20)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[name] if is_c else native)|1,0x600000,count=100)
   traces.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert traces[0]==traces[1],(name,traces)
 print(f'PASS {len(CASES)} compiled-C/native LV flex dimension cases')
