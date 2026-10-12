"""Actual ARM C/native vendor stack option state and MMIO transfer cases."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stack_option.c'
SHIM='''#include <stdint.h>
void audio_ble_vendor_irq_off_47f5b8(uint32_t x){(void)x;}
void audio_ble_vendor_irq_on_47f7ae(uint32_t x){(void)x;}
int32_t audio_ble_vendor_irq_disable_4c44bc(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_ble_vendor_irq_enable_4c4530(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
void audio_ble_vendor_option_before_store_55c13a(void*p){(void)p;}
void audio_ble_vendor_option_after_load_55c168(void*p){(void)p;}
int32_t audio_ble_vendor_wait_480826(uint32_t n,const void*p,uint32_t m,uint32_t v,...){(void)n;(void)p;(void)m;(void)v;return 0;}
'''
NATIVE={'irqoff':0x47f5b8,'irqon':0x47f7ae,'disable':0x4c44bc,'enable':0x4c4530,'before':0x55c13a,'after':0x55c168,'wait':0x480826}
CNAME={'irqoff':'audio_ble_vendor_irq_off_47f5b8','irqon':'audio_ble_vendor_irq_on_47f7ae','disable':'audio_ble_vendor_irq_disable_4c44bc','enable':'audio_ble_vendor_irq_enable_4c4530','before':'audio_ble_vendor_option_before_store_55c13a','after':'audio_ble_vendor_option_after_load_55c168','wait':'audio_ble_vendor_wait_480826'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_stack_option_55c7e8',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,op,enabled,flags,pending,saveflag in [('null',0,0,0,0,0),('badmagic',0,0,0x12345678,0,0),('store_guard',0,1,0x01123456,0,0),('store_plain',0,0,0x01123456,0,0),('store_enabled',0,1,0x01123456,0,1),('store_active',0,1,0x03123456,0,1),('invalid_op',3,0,0x01123456,0,0),('load_busy',1,0,0x03123456,1,0),('load_plain',1,0,0x01123456,0,0),('load_enabled',2,1,0x01123456,0,0),('load_after',2,1,0x01123456,0,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;u.mem_write(row,b'\x00'*0x8a8);u.mem_write(row,struct.pack('<II',flags,1));u.mem_write(row+0x24,struct.pack('<I',pending));u.mem_write(row+0x868,bytes([saveflag]));u.mem_write(row+0x87c,struct.pack('<I',1))
   for off in (0x104,0x118,0x11c,0x200,0x210,0x228,0x22c,0x234,0x23c,0x240,0x244,0x248,0x280,0x2c0):u.mem_write(0x40051000+off,struct.pack('<I',(0x77770000|off)|(1 if label=='load_after' and off==0x228 else 0)))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if label=='null' else row);u.reg_write(UC_ARM_REG_R1,op);u.reg_write(UC_ARM_REG_R2,enabled);u.reg_write(UC_ARM_REG_R3,0x87654321)
   cuts={v:k for k,v in (NATIVE if not is_c else {k:syms[n]&~1 for k,n in CNAME.items()}).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name in ('enable','disable') else 0))
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_radio_stack_option_55c7e8'] if is_c else 0x55c7e8)|1,0x600000,count=2000)
   rows.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,bytes(u.mem_read(row,0x8a8)),bytes(u.mem_read(0x40051000,0x300))))
  assert rows[0]==rows[1],(label,rows[0][:3],rows[1][:3])
  print('PASS',label,rows[0][:3])
