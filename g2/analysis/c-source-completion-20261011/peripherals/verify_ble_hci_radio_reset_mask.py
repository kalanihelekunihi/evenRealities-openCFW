"""Actual ARM C/native vendor reset and sixteen pin-route branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_reset_mask.c'
SHIM='''#include <stdint.h>
uint32_t audio_ble_hci_radio_stack_stop_55c430(uint32_t x){(void)x;return 0;}
uint32_t g2_codec_pin_function(uint32_t p,uint32_t c){(void)p;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_mask_4c2e30',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[('reset_null','reset',0,0),('reset_bad','reset',0x12345678,0),('reset_idle','reset',0x01123456,0),('reset_active','reset',0x03123456,0)]+[(f'mask_{i}_{j}','mask',i,j) for i in range(8) for j in (0,1)]+[('mask_alias','mask',0,4),('mask_invalid','mask',0,2),('mask_index','mask',8,0)]
 for label,fn,arg,selector in cases:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20006000;u.mem_write(row,struct.pack('<I',arg)+bytes(20))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,(0 if label=='reset_null' else row) if fn=='reset' else arg);u.reg_write(UC_ARM_REG_R1,selector);u.reg_write(UC_ARM_REG_R3,0x12345678)
   cuts={0x55c430:'stop',0x480f0c:'pin'} if not is_c else {syms['audio_ble_hci_radio_stack_stop_55c430']&~1:'stop',syms['g2_codec_pin_function']&~1:'pin'};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0) if name=='pin' else 0,uc.reg_read(UC_ARM_REG_R1) if name=='pin' else 0));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_hci_radio_stack_reset_55c286'] if fn=='reset' else syms['audio_ble_hci_radio_mask_4c2e30']) if is_c else (0x55c286 if fn=='reset' else 0x4c2e30)
   u.emu_start(entry|1,0x600000,count=300)
   rows.append((u.reg_read(UC_ARM_REG_R0) if fn=='reset' else None,u.reg_read(UC_ARM_REG_R1) if fn=='reset' else None,calls,bytes(u.mem_read(row,24))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,[c[1] for c in rows[0][2]])
