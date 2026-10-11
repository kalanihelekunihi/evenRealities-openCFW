#!/usr/bin/env python3
"""Bounded native/source ADC open and close configuration comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
folder=R/'g2/components/case/startup_candidate_20261011';obj=H/'application_policy_adc_config.oracle.o';regobj=H/'application_policy_adc_register.config_oracle.o';stub=H/'application_policy_adc_config.oracle_stub.c';stubobj=H/'application_policy_adc_config.oracle_stub.o';elf=H/'application_policy_adc_config.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(folder/'application_policy_adc_config_candidate.c'),'-o',str(obj)],check=True)
subprocess.run(flags+[str(folder/'application_policy_adc_register_candidate.c'),'-o',str(regobj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(regobj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x7a8);counts={}
for name,naddr in [('open_config',0x080007a8),('close_stop',0x080006d4),('close_config',0x08000734)]:
 counts[name]=0
 for i in range(80):
  handle=bytearray(rng.randrange(256) for _ in range(0x70));base=bytearray(rng.randrange(256) for _ in range(0x50))
  struct.pack_into('<I',handle,0,0x40010000);handle[0x19]=1 if i%4==0 else 0
  mode=i%8
  if name=='open_config':
   reg=[0,0x80000000,2,4,0,0,0,0][mode];struct.pack_into('<I',base,8,reg);struct.pack_into('<I',base,0,1 if mode>=4 else 0)
  elif name=='close_stop':
   reg=[0,4,6,4,0,4,6,4][mode];struct.pack_into('<I',base,8,reg)
  else:
   reg=[0,1,3,5,1,1,0,1][mode];struct.pack_into('<I',base,8,reg)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x200008e4,bytes(handle));u.mem_write(0x20000120,struct.pack('<I',1))
   u.mem_map(0x40010000,0x10000);u.mem_write(0x40010000,bytes(base));u.mem_write(0x40012708,struct.pack('<I',0))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x200008e4)
   tick=[0]
   def hook(uc,addr,size,_):
    if addr!=(0x08004eac if native else sym['case_policy_adc_tick']&~1):return
    # The native tick routine is cut at the same boundary as its source copy.
    tick[0]+=1
    uc.reg_write(UC_ARM_REG_R0,tick[0]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((naddr if native else sym['case_policy_adc_'+name])|1,0x20001000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200008e4,0x70)),bytes(u.mem_read(0x40010000,0x50))))
  assert pair[0]==pair[1],(name,i,pair[0][0],pair[1][0])
  counts[name]+=1
print('PASS_CASE_POLICY_ADC_CONFIG',counts)
