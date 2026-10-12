"""Actual ARM C/native vendor option linked-node and DMA callbacks."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_option_children.c'
SHIM='''#include <stdint.h>
void audio_ble_vendor_dma_release_538e3c(uint32_t p){(void)p;}
void audio_ble_vendor_dma_resume_538e8c(uint32_t p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_option_before_store_55c13a',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,pending in [('before_link',0),('before_skip',1),('after',0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;node=0x20009000;u.mem_write(row,b'\x00'*0x8a8);u.mem_write(row+4,struct.pack('<I',1));u.mem_write(row+0x24,struct.pack('<I',pending));u.mem_write(row+0x828,struct.pack('<I',0x2000a000));u.mem_write(node,b'\x55'*8);u.mem_write(0x4005122c,struct.pack('<I',node))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,row)
   cuts={0x538e3c:'release',0x538e8c:'resume'} if not is_c else {syms['audio_ble_vendor_dma_release_538e3c']&~1:'release',syms['audio_ble_vendor_dma_resume_538e8c']&~1:'resume'};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_vendor_option_after_load_55c168'] if label=='after' else syms['audio_ble_vendor_option_before_store_55c13a']) if is_c else (0x55c168 if label=='after' else 0x55c13a)
   u.emu_start(entry|1,0x600000,count=150)
   rows.append((calls,bytes(u.mem_read(node,8))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0])
