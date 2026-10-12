"""Actual compiled-C/native flex track-scan bounded fixed/grow cases."""
from pathlib import Path
import re,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_track_scan.c';CODE=SRC.read_text()
SHIM='#include <stdint.h>\ntypedef struct {uint8_t main_place,cross_place,track_place,flags;} Flex;\ntypedef struct {int32_t cross_size,main_size,fix_main_size;uint32_t item_count;void *grow_dsc;uint32_t grow_count,flags;} Track;\n'
PAIRS={}
for decl in re.findall(r'^extern (.+);',CODE,re.M):
 decl=decl.split(' /*')[0];sym=re.search(r'\b(audio_uart_[a-zA-Z0-9_]+)\s*\(',decl).group(1)
 if '_Noreturn ' in decl:SHIM+=decl.replace('_Noreturn ','')+'{for(;;){}}\n'
 else:SHIM+=decl+('{}' if decl.startswith('void ') and not decl.startswith('void *') else '{return 0;}')+'\n'
 if re.search(r'_[0-9a-f]{6}$',sym):PAIRS[sym]=int(sym[-6:],16)
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wno-c23-extensions','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_find_track_end_48be22',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for count,grow in ((0,0),(1,0),(1,2)):
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;flex=0x20003100;track=0x20003200;item=0x20003300;spec=0x20003400;items=0x20003500
   u.mem_write(obj+8,struct.pack('<I',spec));u.mem_write(spec,struct.pack('<I',items));u.mem_write(spec+0x30,struct.pack('<H',count));u.mem_write(items,struct.pack('<I',item))
   u.mem_write(flex,b'\x00\x00\x00\x01');u.mem_write(track,b'\x77'*24+b'\x00'*4)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in ((UC_ARM_REG_R0,obj),(UC_ARM_REG_R1,flex),(UC_ARM_REG_R2,0),(UC_ARM_REG_R3,100)):
    u.reg_write(reg,val)
   u.mem_write(0x200ff000,struct.pack('<II',3,track))
   mapping={(syms[s]&~1 if is_c else a):s for s,a in PAIRS.items()};calls=[]
   def hook(uc,a,size,_):
    if a not in mapping:return
    n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if n=='audio_uart_lv_child_get_44dce2':ret=item if count and r1==0 else 0
    else:ret={'audio_uart_lv_flex_width_48b90a':20,'audio_uart_lv_flex_height_48b928':30,
              'audio_uart_lv_flex_grow_48b9fc':grow,'audio_uart_lv_flex_min_width_48b914':4,
              'audio_uart_lv_flex_min_height_48b91e':5,'audio_uart_lv_flex_width_margin_48c7b4':25,
              'audio_uart_lv_flex_height_margin_48c7d8':35}.get(n,0)
    calls.append(n.removeprefix('audio_uart_lv_'))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_uart_lv_find_track_end_48be22'] if is_c else 0x48be22)|1,0x600000,count=500)
   traces.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(flex,4)),bytes(u.mem_read(track,28))))
  assert traces[0]==traces[1],(count,grow,traces)
 print('PASS 3 compiled-C/native LV flex track-scan cases')
