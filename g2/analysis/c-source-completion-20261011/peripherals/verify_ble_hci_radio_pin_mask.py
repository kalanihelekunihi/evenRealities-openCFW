"""Compiled ARM C/native GPIO interrupt mask branch effects and error returns."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_pin_mask.c'
SHIM='''#include <stdint.h>
uint32_t g2_power_critical_save(void){return 0;}
void g2_power_critical_restore(uint32_t p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_pin_mask_4810b0',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native_restore={0x4812ea,0x48145e,0x4814ea,0x48152a,0x481568,0x4815e8}
 cases=[('null',0,0,0),('badop',0,4,0x75),('badpin',0,1,0xe0),('set_a',0,1,0x75),('clear_b',1,0,0x75),('set_both',2,1,0x75),('set_a_bank3',3,1,0x75),('mask_clear',2,2,0),('mask_set',2,3,0)]
 for label,bank,op,pin in cases:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   for base in (0x40010530,0x400105a0):
    for i in range(7):u.mem_write(base+0x10*i,struct.pack('<I',0x55aa55aa))
   ptr=0 if label=='null' else 0x20006000
   if ptr:u.mem_write(ptr,struct.pack('<7I',*([pin] if op<2 else [1,2,4,8,16,32,64])+[0]*(6 if op<2 else 0)))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,bank);u.reg_write(UC_ARM_REG_R1,op);u.reg_write(UC_ARM_REG_R2,ptr)
   cuts={0x473940:'save'} if not is_c else {syms['g2_power_critical_save']&~1:'save',syms['g2_power_critical_restore']&~1:'restore'}
   calls=[]
   def hook(uc,a,size,_):
    if not is_c and a in native_restore:uc.reg_write(UC_ARM_REG_PC,(a+4)|1);return
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    if name=='save':uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_radio_pin_mask_4810b0'] if is_c else 0x4810b0)|1,0x600000,count=2500)
   rows.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x40010530,0x70)),bytes(u.mem_read(0x400105a0,0x70))))
  assert rows[0][0]==rows[1][0] and rows[0][2:]==rows[1][2:],(label,rows)
  print('PASS',label,rows[0][0],rows[0][1],rows[1][1])
