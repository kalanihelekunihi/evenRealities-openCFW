"""Actual compiled-C/native flex_update bounded child-order and track effects."""
from pathlib import Path
import re,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_update.c'
CODE=SRC.read_text()
SHIM='#include <stdint.h>\ntypedef struct {uint8_t main_place,cross_place,track_place,flags;} Flex;\ntypedef struct {int32_t cross_size,main_size,fix_main_size;uint32_t item_count;void *grow_dsc;uint32_t grow_count,flags;} Track;\n'
for decl in re.findall(r'^extern (.+);$',CODE,re.M):
 SHIM+=decl+('{}' if decl.startswith('void ') else '{return 0;}')+'\n'
PAIRS={}
for decl in re.findall(r'^extern (.+);$',CODE,re.M):
 sym=re.search(r'\b(audio_uart_[a-zA-Z0-9_]+)\s*\(',decl).group(1)
 addr=int(sym[-6:],16) if re.search(r'_[0-9a-f]{6}$',sym) else 0x44f758
 PAIRS[sym]=(addr,sym)
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wno-c23-extensions','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_theme_default_apply_48bae4',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for count,flow,rtl,place in ((0,0,0,0),(1,0,0,0),(1,1,1,0),(1,8,0,1)):
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;spec=0x20003100
   u.mem_write(obj+8,struct.pack('<I',spec));u.mem_write(obj+0x14,struct.pack('<ii',1000,2000))
   u.mem_write(spec+0x30,struct.pack('<H',count))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   mapping={(syms[s]&~1 if is_c else a):s for a,s in PAIRS.values()};call=[]
   def hook(uc,a,size,_):
    if a not in mapping:return
    n=mapping[a];short=n.removeprefix('audio_uart_lv_');r0=uc.reg_read(UC_ARM_REG_R0)
    if n=='audio_uart_lv_find_track_end_48be22':
     track=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP)+4,4))[0]
     uc.mem_write(track,struct.pack('<iiiiiii',30,0,0,1,0,0,1))
     call.append((short,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
    elif n=='audio_uart_lv_children_repos_48c14e':call.append((short,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
    elif n=='audio_uart_lv_obj_event_451670':call.append((short,uc.reg_read(UC_ARM_REG_R1)))
    else:call.append(short)
    returns={'audio_uart_lv_flex_pad_column_48b96e':2,'audio_uart_lv_flex_pad_row_48b978':3,
             'audio_uart_lv_obj_content_width_43fe16':100,'audio_uart_lv_obj_content_height_43fe70':200,
             'audio_uart_lv_flex_space_top_48ba36':5,'audio_uart_lv_flex_space_left_48ba08':7,
             'audio_uart_lv_flex_width_48b90a':20,'audio_uart_lv_flex_height_48b928':30,
             'audio_uart_lv_find_track_end_48be22':(-1 if flow&8 else count),
             'audio_uart_lv_flex_flow_48b9cc':flow,
             'audio_uart_lv_flex_base_dir_48b9c0':rtl,
             'audio_uart_lv_flex_track_place_48b9f0':place}
    uc.reg_write(UC_ARM_REG_R0,returns.get(n,0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_uart_lv_theme_default_apply_48bae4'] if is_c else 0x48bae4)|1,0x600000,count=400)
   traces.append(call)
  assert traces[0]==traces[1],(count,flow,rtl,place,traces)
 print('PASS 4 compiled-C/native LV flex update cases')
