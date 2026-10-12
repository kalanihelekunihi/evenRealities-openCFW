"""Actual compiled-C/native LV flex selector ABI and value-width checks."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_selectors.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){return 0;}
int32_t audio_uart_lv_flex_space_top_base_48b95a(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_flex_space_left_base_48b964(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_flex_space_offset_48b9aa(void*a,uint32_t b){return 0;}
uint32_t audio_uart_lv_flex_space_flags_48b9b4(void*a,uint32_t b){return 0;}
'''
CASES=[(0x48b9cc,'audio_uart_lv_flex_flow_48b9cc',0x7a,True),
       (0x48b9d8,'audio_uart_lv_flex_main_place_48b9d8',0x7b,True),
       (0x48b9e4,'audio_uart_lv_flex_cross_place_48b9e4',0x7c,True),
       (0x48b9f0,'audio_uart_lv_flex_track_place_48b9f0',0x7d,True),
       (0x48b9c0,'audio_uart_lv_flex_base_dir_48b9c0',0x27,True),
       (0x48b96e,'audio_uart_lv_flex_pad_column_48b96e',0x14,False),
       (0x48b978,'audio_uart_lv_flex_pad_row_48b978',0x15,False),
       (0x48b90a,'audio_uart_lv_flex_width_48b90a',1,False),
       (0x48b928,'audio_uart_lv_flex_height_48b928',2,False)]
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_flex_flow_48b9cc',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for native,name,prop,byte in CASES:
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,5)
   lower=(syms['audio_uart_lv_style_property_44bdea']&~1) if is_c else 0x44bdea
   args=[]
   def hook(uc,a,size,_):
    if a!=lower:return
    args.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_R0,0x123456ff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[name] if is_c else native)|1,0x600000,count=30)
   traces.append((args,u.reg_read(UC_ARM_REG_R0)))
  assert traces[0]==traces[1],(name,traces)
  assert traces[0][0]==[(0x20003000,5,prop)]
  assert traces[0][1]==(0xff if byte else 0x123456ff)
 print('PASS 9 compiled-C/native LV flex selector cases')
