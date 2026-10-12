"""Actual compiled-C/native flex allocation assertion log and fault effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_track_alloc_failure.c'
SHIM='''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){}
'''
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_flex_grow_alloc_failure',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 traces=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  log_addr=(syms['audio_uart_lvgl_log']&~1) if is_c else 0x44d25c
  calls=[];faults=[]
  def cstr(uc,p):return bytes(uc.mem_read(p,256)).split(b'\0')[0].decode()
  def code(uc,a,size,_):
   if a!=log_addr:return
   sp=uc.reg_read(UC_ARM_REG_SP)
   ptrs=struct.unpack('<III',uc.mem_read(sp,12))
   calls.append((uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),
                 uc.reg_read(UC_ARM_REG_R2),cstr(uc,uc.reg_read(UC_ARM_REG_R3)),
                 tuple(cstr(uc,p) for p in ptrs)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def badwrite(uc,access,a,size,value,_):faults.append((a,size,value));return False
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,badwrite)
  try:u.emu_start((syms['audio_uart_lv_flex_grow_alloc_failure'] if is_c else 0x48c026)|1,0x600000,count=60)
  except UcError:pass
  traces.append((calls,faults[:1]))
 assert traces[0]==traces[1],traces
 assert traces[0][1]==[(0xffffffff,4,0)]
 print('PASS 1 compiled-C/native LV flex allocation failure case')
