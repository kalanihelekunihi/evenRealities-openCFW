"""Actual compiled-C/native WSF timer init and callback branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t calls[8],n,ready_args;
void *audio_freertos_timer_create_dynamic(const char *name,uint32_t period,uint32_t reload,uintptr_t id,void (*cb)(void *)){(void)name;(void)period;(void)reload;(void)id;(void)cb;calls[n++]=1;return (void *)0x20080000;}
uint32_t audio_tick(void){calls[n++]=2;return 1234;}
void audio_wsf_task_set_ready(uint8_t h,uint8_t f){ready_args=((uint32_t)h<<8)|f;calls[n++]=3;}
uint32_t audio_wsf_interrupt_mask_set(void){return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfTimerInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_timer_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for existing in [False,True]:
  results=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   listed,handle,tick=(syms[x] for x in ('audio_wsf_timer_list','audio_wsf_timer_handle','audio_wsf_timer_last_tick')) if c else (0x200741b0,0x20074ef4,0x20074ef8)
   u.mem_write(listed,b'\xaa'*8);u.mem_write(handle,struct.pack('<I',0x20081000 if existing else 0));u.mem_write(tick,struct.pack('<I',55));trace=[]
   if not c:
    def hook(uc,a,size,_):
     if a==0x47e6dc:
      assert uc.reg_read(UC_ARM_REG_R1)==10 and uc.reg_read(UC_ARM_REG_R2)==0 and uc.reg_read(UC_ARM_REG_R3)==0
      trace.append(1);uc.reg_write(UC_ARM_REG_R0,0x20080000)
     elif a==0x454efe:trace.append(2);uc.reg_write(UC_ARM_REG_R0,1234)
     elif a==0x52b95e:trace.append(3)
     else:return
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['WsfTimerInit'] if c else 0x52a474)|1,0x600000,count=3000)
   if c:
    n=struct.unpack('<I',u.mem_read(syms['n'],4))[0]
    trace=list(struct.unpack('<'+str(n)+'I',u.mem_read(syms['calls'],n*4)))
   results.append((bytes(u.mem_read(listed,8)),struct.unpack('<I',u.mem_read(handle,4))[0],struct.unpack('<I',u.mem_read(tick,4))[0],trace))
  assert results[0]==results[1],(existing,results)
  print('PASS WSF timer init',existing)
 for c in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if not c:
   def cut(uc,a,size,_):
    if a==0x52b95e:
     assert uc.reg_read(UC_ARM_REG_R0)==0 and uc.reg_read(UC_ARM_REG_R1)==2
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut)
  u.emu_start((syms['audio_wsf_timer_callback'] if c else 0x52a468)|1,0x600000,count=1000)
  if c:assert struct.unpack('<I',u.mem_read(syms['ready_args'],4))[0]==2
 print('PASS WSF timer callback')
