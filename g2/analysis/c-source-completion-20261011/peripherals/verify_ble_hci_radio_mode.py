"""Actual ARM C/native radio mode mapping and watchdog wrapper."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_mode.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_radio_mode_cells_20074368[3];
void audio_ble_npmx_kick_watchdog_5118e8(void){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_mode_state_50938e',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,arg in [('mode0',0),('mode1',1),('mode2',2),('mode3',3),('mode_wrap',256),('kick',0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R7,0x12345678);u.reg_write(UC_ARM_REG_R0,arg)
   cut=(syms['audio_ble_npmx_kick_watchdog_5118e8']&~1) if is_c else 0x5118e8;calls=[]
   def hook(uc,a,size,_):
    if a!=cut:return
    calls.append('kick');uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_hci_radio_state_prepare_5118e0'] if is_c else 0x5118e0) if label=='kick' else (syms['audio_ble_hci_radio_mode_state_50938e'] if is_c else 0x50938e)
   u.emu_start(entry|1,0x600000,count=150)
   v=u.reg_read(UC_ARM_REG_R0)
   if label!='kick':v-=syms['audio_ble_hci_radio_mode_cells_20074368'] if is_c else 0x20074368
   rows.append((v,calls))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0])
