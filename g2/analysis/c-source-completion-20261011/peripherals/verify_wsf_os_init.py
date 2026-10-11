"""Actual compiled-C/native Cordio WsfOsInit state and create call."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t calls;
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){for(uint32_t i=0;i<n;i++)((uint8_t *)p)[i]=(uint8_t)v;}
void *audio_uart_event_dynamic_create(void){calls++;return (void *)0x20080000;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_wsf_os_initialize',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_os_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for existing in [False,True]:
  results=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);state=syms['audio_wsf_task_state'] if c else 0x20073230;cell=syms['audio_wsf_event_group'] if c else 0x20074ef0
   u.mem_write(state,b'\xaa'*0x40);u.mem_write(cell,struct.pack('<I',0x20080100 if existing else 0));calls=[0]
   if not c:
    def hook(uc,a,size,_):
     if a==0x47ebd8:
      calls[0]+=1;uc.reg_write(UC_ARM_REG_R0,0x20080000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_wsf_os_initialize'] if c else 0x52b9b2)|1,0x600000,count=5000)
   if c:calls[0]=struct.unpack('<I',u.mem_read(syms['calls'],4))[0]
   results.append((bytes(u.mem_read(state,0x40)),struct.unpack('<I',u.mem_read(cell,4))[0],calls[0]))
  assert results[0]==results[1],(existing,results)
  print('PASS WSF OS init',existing)
