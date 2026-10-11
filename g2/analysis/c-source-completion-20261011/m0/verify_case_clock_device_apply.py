#!/usr/bin/env python3
"""Bounded CASE 0x52e4 clock device apply original/C comparison."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_clock_device_apply_candidate.c'
table=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_clock_tables_candidate.c'
obj=H/'clock_device_apply.oracle.o';tabobj=H/'clock_device_apply.table.o';stub=H/'clock_device_apply.oracle_stub.c';stubobj=H/'clock_device_apply.oracle_stub.o';elf=H/'clock_device_apply.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for a,b in [(src,obj),(table,tabobj)]:subprocess.run(flags+[str(a),'-o',str(b)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_adc_tick(void){return 100;}\nuint32_t case_boot_sensor_clock_549c(void){return 16000000;}\nuint32_t case_transfer_clock_config(uint32_t x){return x^0x31415926u;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(tabobj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x52e4)
for i in range(96):
 cfg=[rng.getrandbits(32) for _ in range(4)];cfg[0]=[0,2,4,6][i%4]
 latency=i%7;baseline=bytearray(rng.randbytes(0x80));baseline[:4]=struct.pack('<I',(struct.unpack('<I',baseline[:4])[0]&~7)|latency)
 # Low latency already matches, so this tests no-wait paths and PLL/prescaler fields.
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x40022000,0x1000)
  u.mem_write(0x20003000,struct.pack('<4I',*cfg));u.mem_write(0x2000011c,struct.pack('<I',0x12345678))
  u.mem_write(0x40021000,bytes(baseline));u.mem_write(0x40022000,struct.pack('<I',latency))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,latency)
  targets=({0x08004eac:'tick',0x0800549c:'clock',0x08004f14:'plan'} if native else {sym['case_policy_adc_tick']&~1:'tick',sym['case_boot_sensor_clock_549c']&~1:'clock',sym['case_transfer_clock_config']&~1:'plan'})
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   uc.reg_write(UC_ARM_REG_R0,100 if kind=='tick' else 16000000 if kind=='clock' else uc.reg_read(UC_ARM_REG_R0)^0x31415926)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080052e4 if native else sym['case_boot_clock_device_apply'])|1,0x20008000,count=3000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x40021000,0x80)),bytes(u.mem_read(0x40022000,4)),bytes(u.mem_read(0x20000124,4))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0],[(j,a,b) for j,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:8],pair[0][3],pair[1][3])
print('PASS_CASE_CLOCK_DEVICE_APPLY',96)
