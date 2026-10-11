"""Actual ARM compiled-C/native HCI radio shutdown sequence comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_shutdown.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_radio_timer[32];
volatile uint8_t audio_ble_hci_radio_active,audio_ble_hci_radio_pending;
volatile uint32_t audio_ble_hci_radio_context_ptr;
void WsfTimerStop(void*a){(void)a;}
void audio_ble_hci_radio_disable_52dd6a(void){}
void audio_ble_hci_radio_switch_52eece(uint8_t a){(void)a;}
void audio_ble_hci_radio_pins_52dd7c(void){}
uint32_t audio_ble_hci_radio_reset_52df12(void*a){(void)a;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_driver_radio_shutdown',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for active,pending in ((0,0),(1,1),(0xff,0x80)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   timer=syms['audio_ble_hci_radio_timer'] if compiled else 0x20073e64
   ac=syms['audio_ble_hci_radio_active'] if compiled else 0x20074638
   pe=syms['audio_ble_hci_radio_pending'] if compiled else 0x2007463c
   context=syms['audio_ble_hci_radio_context_ptr'] if compiled else 0x20074630
   u.mem_write(ac,bytes([active]));u.mem_write(pe,bytes([pending]));u.mem_write(context,struct.pack('<I',0x20005000))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   native={'timer':0x52a4d2,'disable':0x52dd6a,'switch':0x52eece,'pins':0x52dd7c,'reset':0x52df12}
   names={'timer':'WsfTimerStop','disable':'audio_ble_hci_radio_disable_52dd6a','switch':'audio_ble_hci_radio_switch_52eece','pins':'audio_ble_hci_radio_pins_52dd7c','reset':'audio_ble_hci_radio_reset_52df12'}
   cuts={(syms[names[k]]&~1 if compiled else a):k for k,a in native.items()}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    calls.append((k,r0-timer if k=='timer' else r0 if k in ('switch','reset') else 0))
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_driver_radio_shutdown'] if compiled else 0x4b49ce)|1,0x600000,count=700)
   rows.append((calls,bytes(u.mem_read(ac,1)),bytes(u.mem_read(pe,1))))
  assert rows[0]==rows[1],(active,pending,rows)
  print('PASS',active,pending,rows[0])
