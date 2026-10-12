"""Actual ARM C/native DMA channel setup and descriptor MMIO effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_dma_queue.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_dma_channel_rows_2006ef28[12*0x2c];
uint8_t audio_ble_dma_channels_rom_6c0f40[12*0x28];
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_dma_queue_538d58',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,ch,params,out,busy in [('badchan',12,1,1,0),('nullparams',1,0,1,0),('zeroaddr',1,2,1,0),('nullout',1,1,0,0),('small',1,3,1,0),('busy',1,1,1,1),('valid',1,1,1,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x20000)
   for a,d in segs:u.mem_write(a,d)
   base=syms['audio_ble_dma_channel_rows_2006ef28'] if is_c else 0x2006ef28
   table=syms['audio_ble_dma_channels_rom_6c0f40'] if is_c else 0x6c0f40
   if is_c:u.mem_write(table,BLOB[0x6c0f40-0x438000:0x6c0f40-0x438000+12*0x28])
   row=base+ch*0x2c if ch<12 else base
   u.mem_write(row,b'\x00'*0x2c);u.mem_write(row,struct.pack('<I',0x01000000 if busy else 0))
   u.mem_write(0x20006000,struct.pack('<4I',1 if params==3 else 12,0 if params==2 else 0x20009000,1,0x12345678));u.mem_write(0x20007000,b'\x00'*4);u.mem_write(0x40051200,b'\xaa'*0x60)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ch);u.reg_write(UC_ARM_REG_R1,0 if params==0 else 0x20006000);u.reg_write(UC_ARM_REG_R2,0 if out==0 else 0x20007000)
   u.emu_start((syms['audio_ble_vendor_dma_queue_538d58'] if is_c else 0x538d58)|1,0x600000,count=500)
   result=struct.unpack('<I',u.mem_read(0x20007000,4))[0];result=(result-base)&0xffffffff if result else 0
   channel=bytearray(u.mem_read(row,0x2c));entry=struct.unpack_from('<I',channel,36)[0]
   if entry:struct.pack_into('<I',channel,36,(entry-table)&0xffffffff)
   rows.append((u.reg_read(UC_ARM_REG_R0),result,bytes(channel),bytes(u.mem_read(0x40051200,0x60))))
  assert rows[0]==rows[1],(label,rows[0][:2],rows[1][:2])
  print('PASS',label,rows[0][:2])
