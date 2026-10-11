"""Bounded actual C/native CMSIS osEventFlagsSet branch comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CASES=[('null',0,1,0,1,0),('bad_mask',0x20010000,0x80000000,0,1,0),
       ('task',0x20010000,3,0,1,0),('isr_fail',0x20010000,3,1,0,0),
       ('isr_ok',0x20010000,3,1,1,0),('isr_wake',0x20010000,3,1,1,1)]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t g_irq,g_pass,g_wake;
uint32_t audio_irq_context(void){return g_irq;}
uint32_t xEventGroupSetBits(void *p,uint32_t bits){(void)p;(void)bits;return 0x123400u;}
int32_t xEventGroupSetBitsFromISR(void *p,uint32_t bits,int32_t *wake){(void)p;(void)bits;*wake=(int32_t)g_wake;return (int32_t)g_pass;}
uint32_t audio_uart_event_get_isr(void *p){(void)p;return 0x10u;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,osEventFlagsSet',str(ROOT/'components/audio/uart_thread_source_candidate/cmsis_event_flags_set.c'),str(shim),'-o',str(elf)],check=True)
 symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,case):
  label,group,bits,irq,passed,wake=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x1000)
  for name,value in [('g_irq',irq),('g_pass',passed),('g_wake',wake)]:
   u.mem_write(symbols[name],struct.pack('<I',value))
  u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,bits)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if not candidate:
   def cut(uc,address,size,_):
    if address==0x44900e:value=irq
    elif address==0x47ed76:value=0x123400
    elif address==0x47ee4a:
     uc.mem_write(uc.reg_read(UC_ARM_REG_R2),struct.pack('<I',wake));value=passed
    elif address==0x47ed64:value=0x10
    else:return
    uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut)
  u.emu_start((symbols['osEventFlagsSet'] if candidate else 0x4495e4)|1,0x600000,count=2000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0xe000ed04,4))
 for case in CASES:
  a=run(False,case);b=run(True,case)
  assert a==b,(case[0],a,b)
  print('PASS CMSIS event set',case[0])
