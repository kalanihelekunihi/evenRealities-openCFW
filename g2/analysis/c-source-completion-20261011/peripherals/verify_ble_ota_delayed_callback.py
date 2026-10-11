"""Actual ARM C/native OTA delayed WSF callback comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_ota_delayed_callback.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ota_handler_state[4];
unsigned audio_log_level(void){return 0;}
void audio_log_extended(){}
unsigned compressed_log_output(){return 0;}
void *audio_wsf_msg_alloc(){return 0;}
void audio_wsf_msg_send(){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_delayed_callback',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for allocated,flags in ((False,0),(True,0),(True,2),(True,1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=(syms['audio_ble_ota_handler_state']&~1) if compiled else 0x200748b4
   u.mem_write(state,b'\x07\x09\x00\x00');u.mem_write(0x20001000,b'X'*12)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={(syms[k]&~1 if compiled else v):k for k,v in {
     'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,
     'audio_wsf_msg_alloc':0x4bf99e,'audio_wsf_msg_send':0x4bf9ba}.items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a]
    if k=='audio_wsf_msg_send':calls.append((k,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(0x20001000,12))))
    elif k=='audio_wsf_msg_alloc':calls.append((k,uc.reg_read(UC_ARM_REG_R0)))
    else:calls.append((k,))
    uc.reg_write(UC_ARM_REG_R0,flags if k=='audio_log_level' else 0x20001000 if k=='audio_wsf_msg_alloc' and allocated else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((syms['audio_ble_ota_delayed_callback'] if compiled else 0x4bdb38)|1,0x600000,count=500)
   rows.append(calls)
  assert rows[0]==rows[1],(allocated,flags,rows)
  print('PASS',allocated,flags,rows[0])
