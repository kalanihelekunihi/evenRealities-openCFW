"""Compiled-C/native cancellation and ring-event forwarder."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
volatile uint8_t audio_ble_master_connect_state;
void audio_ble_master_connect_event(void){}
uint32_t audio_event_loop_remove_delayed(void(*a)(void)){(void)a;return 0;}
void audio_ble_master_emit_ring_event(uint8_t a){(void)a;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_cancel_retry',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_cancel.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for prior in (0,1,2):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_master_connect_state'] if compiled else 0x20074f87;u.mem_write(state,bytes([prior]))
   cuts={syms['audio_ble_master_emit_ring_event']&~1:'event',syms['audio_event_loop_remove_delayed']&~1:'remove'} if compiled else {0x4ac16c:'event',0x476ace:'remove'}
   calls=[]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if kind=='event':calls.append(('event',uc.reg_read(UC_ARM_REG_R0)))
    elif kind=='remove':calls.append(('remove',uc.reg_read(UC_ARM_REG_R0)==((syms['audio_ble_master_connect_event'] if compiled else 0x4a1b60)|1)))
    else:return
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_master_cancel_retry'] if compiled else 0x4a17f4)|1,0x600000,count=500)
   observations.append((u.mem_read(state,1)[0],calls))
  assert observations[0]==observations[1],(prior,observations)
  print('PASS master cancel state',prior)
