#!/usr/bin/env python3
"""Controlled native/source ADC open, settle, read, close comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_adc_lowers_candidate.c';obj=H/'application_policy_adc_lowers.oracle.o';stub=H/'application_policy_adc_lowers.oracle_stub.c';stub_obj=H/'application_policy_adc_lowers.oracle_stub.o';elf=H/'application_policy_adc_lowers.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_policy_adc_ready','case_policy_adc_open_config','case_policy_adc_close_stop','case_policy_adc_close_config','case_policy_adc_tick','case_policy_adc_special']
stub.write_text('#include <stdint.h>\n'+'\n'.join('uint32_t '+n+'(uint32_t x){(void)x;return 0;}' for n in names)+'\n')
subprocess.run(flags+[str(stub),'-o',str(stub_obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stub_obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={0x0800678a:'ready',0x080007a8:'open_config',0x080006d4:'close_stop',0x08000734:'close_config',0x08004eac:'tick',0x08006792:'special'}
source={sym[n]&~1:k for n,k in zip(names,['ready','open_config','close_stop','close_config','tick','special'])}
entries={'open':(0x080047d4,'case_policy_adc_open'),'settle':(0x08004710,'case_policy_adc_settle'),'read':(0x08004328,'case_policy_adc_read'),'close':(0x0800483c,'case_policy_adc_close')}
rng=random.Random(0x47d4);counts={x:0 for x in entries}
for kind in entries:
 for i in range(80):
  handle=bytearray(rng.randrange(256) for _ in range(0x70));base=bytearray(rng.randrange(256) for _ in range(0x50))
  struct.pack_into('<I',handle,0,0x40010000)
  handle[0x54]=[0,1,2][i%3];handle[0x18]=i&1;handle[0x1a]=(i>>1)&1
  struct.pack_into('<I',handle,0x14,8 if i&1 else 4)
  reg=4 if i&1 else 8
  struct.pack_into('<I',base,0,reg | (8 if i&4 else 0))
  struct.pack_into('<I',base,12,0 if i&1 else 1)
  returns={'ready':i%3==0,'open_config':i%5==0 and 7,'close_stop':i%7==0 and 9,'close_config':i%11==0 and 6,'special':i%2,'tick':0}
  pair=[]
  for is_native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x200008e4,bytes(handle))
   u.mem_map(0x40010000,0x1000);u.mem_write(0x40010000,bytes(base))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x200008e4);u.reg_write(UC_ARM_REG_R1,3)
   trace=[];tick=0
   def hook(uc,addr,size,_):
    name=(native if is_native else source).get(addr)
    if name is None:return
    trace.append((name,) if name=='tick' else (name,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_R0,returns[name] if name!='tick' else len([x for x in trace if x[0]=='tick']))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=entries[kind][0] if is_native else sym[entries[kind][1]]
   u.emu_start(entry|1,0x20001000,count=2000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200008e4,0x70)),bytes(u.mem_read(0x40010000,0x50)),trace))
  assert pair[0]==pair[1],(kind,i,pair[0][0],pair[1][0],pair[0][3],pair[1][3])
  counts[kind]+=1
print('PASS_CASE_POLICY_ADC_LOWERS',counts)
