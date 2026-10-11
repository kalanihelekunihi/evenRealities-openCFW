"""Actual compiled-C/native DmConnRegister and SmpDbInit state branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_dm_connection_registry[0x200],audio_ble_smp_handler_state[0xf0];
void WsfTaskLock(void){}void WsfTaskUnlock(void){}void WsfTimerStop(void *p){(void)p;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *q=p;for(uint32_t i=0;i<n;i++)q[i]=(uint8_t)v;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpDbInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_smp_db_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for event in [0,1,5,255]:
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);base=syms['audio_ble_dm_connection_registry'] if c else 0x200712a4
   u.mem_write(base+0x90+(event&255)*4,b'\x00'*4);events=[]
   targets={syms['WsfTaskLock']&~1:1,syms['WsfTaskUnlock']&~1:2} if c else {0x52b8c8:1,0x52b8d0:2}
   def cut(uc,a,size,_):
    if a in targets:
     events.append(targets[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,0x20088001)
   u.emu_start((syms['DmConnRegister'] if c else 0x4b6c64)|1,0x600000,count=2000)
   out.append((struct.unpack('<I',u.mem_read(base+0x90+(event&255)*4,4))[0],events))
  assert out[0]==out[1],(event,out)
  print('PASS DM conn register',event)
 for timer_active in [False,True]:
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);db=syms['audio_ble_smp_database'] if c else 0x200708ec;state=syms['audio_ble_smp_handler_state'] if c else 0x20070aec
   u.mem_write(db,b'\xaa'*0x100);u.mem_write(db+0xfd,bytes([1 if timer_active else 0]));u.mem_write(state+0xec,b'\x37');calls=[0]
   target=(syms['WsfTimerStop']&~1) if c else 0x52a4d2
   def cut(uc,a,size,_):
    if a==target:
     calls[0]+=1;assert uc.reg_read(UC_ARM_REG_R0)==db+0xf0
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['SmpDbInit'] if c else 0x542288)|1,0x600000,count=5000)
   out.append((bytes(u.mem_read(db,0x100)),calls[0]))
  assert out[0]==out[1],(timer_active,out)
  print('PASS SMP DB init',timer_active)
