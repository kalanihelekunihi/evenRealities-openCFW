"""Actual ARM C/native vendor stack row allocation and stop effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stack_open_stop.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_vendor_stack_rows_2003b558[8*0x8a8];
uint32_t audio_ble_vendor_stack_stop_hal_55c11a(void *row){(void)row;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_stack_open_55c2bc',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,fn,index,flags,pending in [('open_bad_index','open',8,0,0),('open_null','open',1,0,0),('open_busy','open',1,0x01000000,0),('open_ok','open',1,0x00000200,0),('stop_null','stop',0,0,0),('stop_bad','stop',0,0x12345678,0),('stop_inactive','stop',0,0x01123456,0),('stop_pending','stop',0,0x03123456,1),('stop_ok','stop',0,0x03123456,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   base=syms['audio_ble_vendor_stack_rows_2003b558'] if is_c else 0x2003b558
   row=base+0x8a8 if fn=='open' else base;u.mem_write(row,b'\x00'*0x8a8);u.mem_write(row,struct.pack('<I',flags));u.mem_write(row+4,struct.pack('<I',1));u.mem_write(row+0x24,struct.pack('<I',pending))
   u.mem_write(0x4005111c,struct.pack('<I',0xffffffff));u.mem_write(0x20006000,b'\x00'*4)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,index if fn=='open' else (0 if label=='stop_null' else row))
   u.reg_write(UC_ARM_REG_R1,0 if label=='open_null' else 0x20006000)
   cut=(syms['audio_ble_vendor_stack_stop_hal_55c11a']&~1) if is_c else 0x55c11a;calls=[]
   def hook(uc,a,size,_):
    if a!=cut:return
    calls.append(('stop_hal',(uc.reg_read(UC_ARM_REG_R0)-row)&0xffffffff));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_radio_stack_open_55c2bc'] if fn=='open' else syms['audio_ble_hci_radio_stack_stop_55c430']) if is_c else (0x55c2bc if fn=='open' else 0x55c430)
   u.emu_start(entry|1,0x600000,count=250)
   out=struct.unpack('<I',u.mem_read(0x20006000,4))[0];out=(out-base)&0xffffffff if out else 0
   rows.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(row,0x2c)),out,bytes(u.mem_read(0x4005111c,4))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][:2])
