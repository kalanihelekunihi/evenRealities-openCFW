"""Compiled-C/native ring-link enum names and transitions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
volatile uint8_t audio_ble_ring_link_state;
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_set_ring_link_state',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_ring_link_state.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for prior,next_state,level in ((0,0,0),(0,2,0),(2,4,1),(6,7,2),(2,2,4)):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_ring_link_state'] if compiled else 0x20074f85
   u.mem_write(state,bytes([prior]));u.mem_write(0x20090000,b'reason\0')
   cuts={syms['audio_log_level']&~1:'level',syms['audio_log_extended']&~1:'ext',syms['compressed_log_output']&~1:'compact'} if compiled else {0x43d0ce:'level',0x43d574:'ext',0x43ce9e:'compact'}
   events=[]
   def s(addr):return bytes(u.mem_read(addr,160)).split(b'\0')[0]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if kind=='level':uc.reg_write(UC_ARM_REG_R0,level);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif kind=='ext':
     sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');msg=int.from_bytes(uc.mem_read(sp+4,4),'little')
     events.append(('ext',uc.reg_read(UC_ARM_REG_R0),line,s(msg)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif kind=='compact':events.append(('compact',uc.reg_read(UC_ARM_REG_R0),s(uc.reg_read(UC_ARM_REG_R1))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,next_state);u.reg_write(UC_ARM_REG_R1,0x20090000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_set_ring_link_state'] if compiled else 0x49f870)|1,0x600000,count=10000)
   observations.append((u.mem_read(state,1)[0],events))
  assert observations[0]==observations[1],(prior,next_state,level,observations)
  print('PASS ring link transition',prior,next_state,level)
