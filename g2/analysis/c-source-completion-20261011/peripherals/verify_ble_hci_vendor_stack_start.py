"""Actual ARM C/native vendor stack start state, MMIO, failure transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stack_start.c'
SHIM='''#include <stdint.h>
int32_t audio_ble_vendor_stack_start_guard_55bd2e(uint32_t a,uint32_t b){(void)a;(void)b;return 1;}
int32_t audio_ble_vendor_stack_dma_prepare_55c0dc(void*p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;return 0;}
int32_t audio_ble_vendor_wait_480826(uint32_t a,const void*p,uint32_t b,uint32_t c,...){(void)a;(void)p;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_stack_start_55c32e',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'guard':0x55bd2e,'dma':0x55c0dc,'wait':0x480826};compiled={'guard':syms['audio_ble_vendor_stack_start_guard_55bd2e']&~1,'dma':syms['audio_ble_vendor_stack_dma_prepare_55c0dc']&~1,'wait':syms['audio_ble_vendor_wait_480826']&~1}
 for label,flags,count,fail in [('null',0,0,''),('bad',0x12345678,0,''),('active',0x03123456,0,''),('guardfail',0x01123456,0,'guard'),('waitok',0x01123456,0,''),('dmaok',0x01123456,128,''),('dmafail',0x01123456,128,'dma'),('waitfail',0x01123456,128,'wait')]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;u.mem_write(row,b'\x55'*0x8a8);u.mem_write(row,struct.pack('<II',flags,1));u.mem_write(row+8,b'\x01');u.mem_write(row+12,struct.pack('<II',count,24));u.mem_write(0x40051000,b'\xaa'*0x300)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if label=='null' else row);u.reg_write(UC_ARM_REG_R2,0x12345678);u.reg_write(UC_ARM_REG_R3,0x87654321)
   cuts={v:k for k,v in (compiled if is_c else native).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    val=(0 if fail=='guard' else 1) if name=='guard' else (5 if name==fail else 0)
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_radio_stack_start_55c32e'] if is_c else 0x55c32e)|1,0x600000,count=1000)
   rows.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,bytes(u.mem_read(row,0x8a8)),bytes(u.mem_read(0x40051000,0x300))))
  assert rows[0]==rows[1],(label,rows[0][:3],rows[1][:3])
  print('PASS',label,rows[0][:3])
