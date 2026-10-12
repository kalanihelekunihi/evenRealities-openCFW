"""Actual compiled ARM C/native vendor stack config validation/MMIO cases."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stack_config.c'
SHIM='''#include <stdint.h>
uint32_t audio_ble_vendor_clock_divider_55bf64(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_stack_config_55ca94',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[('null_row',0,0x01123456,1,0,100000,0),('bad_magic',1,0x12345678,1,0,100000,0),('null_cfg',1,0x01123456,1,0,100000,1),('bad_index',1,0x01123456,8,0,100000,0),('active',1,0x03123456,1,0,100000,0),('mode0_bad_bits',1,0x01123456,1,0,100000,4),('mode0_bad_rate',1,0x01123456,1,0,0x02dc6c01,0),('mode0_ok',1,0x01123456,1,0,100000,2),('mode1_bad',1,0x01123456,1,1,12345,0),('mode1_100k',1,0x01123456,1,1,0x186a0,0),('mode1_400k',1,0x01123456,1,1,0x61a80,0),('mode1_1m',1,0x01123456,1,1,0xf4240,0)]
 for label,hasrow,flags,index,mode,freq,aux in cases:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;cfg=0x20007000;u.mem_write(row,b'\x00'*0x8a8);u.mem_write(row,struct.pack('<II',flags,index));u.mem_write(cfg,bytes([mode,0,0,0])+struct.pack('<I',freq)+bytes([aux,0,0,0])+struct.pack('<II',128,24))
   u.mem_write(0x40051000,b'\x00'*0x300)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,row if hasrow else 0);u.reg_write(UC_ARM_REG_R1,0 if label=='null_cfg' else cfg)
   cut=(syms['audio_ble_vendor_clock_divider_55bf64']&~1) if is_c else 0x55bf64;calls=[]
   def hook(uc,a,size,_):
    if a!=cut:return
    calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_radio_stack_config_55ca94'] if is_c else 0x55ca94)|1,0x600000,count=600)
   rows.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(row,0x8a8)),bytes(u.mem_read(0x40051000,0x300))))
  assert rows[0]==rows[1],(label,rows[0][:2],rows[1][:2])
  print('PASS',label,rows[0][:2])
