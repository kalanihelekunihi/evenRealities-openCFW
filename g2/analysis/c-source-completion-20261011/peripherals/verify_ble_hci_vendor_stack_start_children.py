"""Actual ARM C/native vendor start guard and DMA-queue composition."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stack_start_children.c'
SHIM='''#include <stdint.h>
int32_t audio_ble_vendor_dma_queue_538d58(uint32_t a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_stack_start_guard_55bd2e',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,fn,regval,mode,child_result in [('guard_low','guard',3,1,0),('guard_high','guard',0x20,1,0),('guard_no','guard',0x0,1,0),('dma_ok','dma',0,0,0),('dma_fail','dma',0,0,5)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;u.mem_write(row,b'\xaa'*0x8a8);u.mem_write(row+4,struct.pack('<I',1));u.mem_write(0x4005111c,struct.pack('<I',regval))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1 if fn=='guard' else row);u.reg_write(UC_ARM_REG_R1,mode if fn=='guard' else 24);u.reg_write(UC_ARM_REG_R2,128);u.reg_write(UC_ARM_REG_R3,0x12345678)
   cut=(syms['audio_ble_vendor_dma_queue_538d58']&~1) if is_c else 0x538d58;calls=[]
   def hook(uc,a,size,_):
    if a!=cut:return
    calls.append((uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),16)),uc.reg_read(UC_ARM_REG_R2)-row))
    uc.reg_write(UC_ARM_REG_R0,child_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_vendor_stack_start_guard_55bd2e'] if fn=='guard' else syms['audio_ble_vendor_stack_dma_prepare_55c0dc']) if is_c else (0x55bd2e if fn=='guard' else 0x55c0dc)
   u.emu_start(entry|1,0x600000,count=200)
   rows.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(row,0x8a8)),bytes(u.mem_read(0x4005111c,4))))
  assert rows[0]==rows[1],(label,rows[0][:2],rows[1][:2])
  print('PASS',label,rows[0][:2])
