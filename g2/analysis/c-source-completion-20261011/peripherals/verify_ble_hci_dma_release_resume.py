"""Actual ARM C/native DMA release/resume flags, MMIO and barrier branch."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_dma_release_resume.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_dma_release_538e3c',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,fn,flags,address in [('release_null','release',0,0),('release_bad','release',0x12345678,0),('release_inactive','release',0x01cdcdcd,0),('release_barrier','release',0x01cdcdcd,0x20080000),('release_active','release',0x03cdcdcd,0),('resume_bad','resume',0x12345678,0),('resume_inactive','resume',0x01cdcdcd,0),('resume_active','resume',0x03cdcdcd,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;desc=0x20007000;u.mem_write(row,b'\x00'*0x2c);u.mem_write(row,struct.pack('<I',flags));u.mem_write(row+8,struct.pack('<I',address));u.mem_write(row+36,struct.pack('<I',desc));u.mem_write(desc,struct.pack('<I',0x40051228));u.mem_write(0x40051228,struct.pack('<I',0xaabbcc02))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if label=='release_null' else row)
   entry=(syms['audio_ble_vendor_dma_release_538e3c'] if fn=='release' else syms['audio_ble_vendor_dma_resume_538e8c']) if is_c else (0x538e3c if fn=='release' else 0x538e8c)
   u.emu_start(entry|1,0x600000,count=100)
   rows.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(row,0x2c)),bytes(u.mem_read(0x40051228,4))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0])
