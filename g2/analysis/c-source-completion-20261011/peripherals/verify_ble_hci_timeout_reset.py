"""Actual ARM compiled-C/native HCI timeout and DM reset comparisons."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_timeout_reset.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[64];
void *audio_wsf_msg_alloc(uint16_t a){(void)a;return 0;}
void audio_wsf_msg_send(uint8_t a,void*b){(void)a;(void)b;}
void audio_ble_hci_driver_radio_shutdown(void){}
void audio_ble_hci_driver_radio_boot(uint8_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_device_reset',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,ready,alloc in (('dm',0,0),('dm',1,0),('dm',1,1),('timeout',1,1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_dm_handler_state'] if compiled else 0x20073b78
   u.mem_write(state+0x10,bytes([ready]));u.mem_write(state+0x0c,b'\x09')
   u.mem_write(0x20004000,b'X'*12)
   u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   native={'alloc':0x4bf99e,'send':0x4bf9ba,'shutdown':0x4b49ce,'boot':0x4b48a6}
   names={'alloc':'audio_wsf_msg_alloc','send':'audio_wsf_msg_send','shutdown':'audio_ble_hci_driver_radio_shutdown','boot':'audio_ble_hci_driver_radio_boot'}
   cuts={(syms[names[k]]&~1 if compiled else a):k for k,a in native.items()}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='alloc':calls.append((k,r0));res=0x20004000 if alloc else 0
    elif k=='send':calls.append((k,r0,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),4))));res=0
    else:calls.append((k,r0 if k=='boot' else 0));res=0
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   start=(syms['audio_ble_dm_device_reset'] if compiled else 0x4b3026) if kind=='dm' else (syms['audio_ble_hci_command_timeout'] if compiled else 0x52aee6)
   u.emu_start(start|1,0x600000,count=700)
   rows.append((calls,bytes(u.mem_read(state+0x0c,5))))
  assert rows[0]==rows[1],(kind,ready,alloc,rows)
  print('PASS',kind,ready,alloc,len(rows[0][0]))
