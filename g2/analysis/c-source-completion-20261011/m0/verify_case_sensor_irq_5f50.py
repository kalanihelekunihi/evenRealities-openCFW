#!/usr/bin/env python3
"""Bounded stock/C CASE sensor IRQ cuts over actual peripheral and descriptor RAM."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_irq_5f50_candidate.c'
obj=H/'sensor_irq_5f50.oracle.o';stub=H/'sensor_irq_5f50.oracle_stub.c';stubobj=H/'sensor_irq_5f50.oracle_stub.o';elf=H/'sensor_irq_5f50.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_sensor_irq_error(uint32_t x){(void)x;}\nuint32_t case_boot_sensor_irq_restart_ready(uint32_t x){(void)x;return 0;}\nvoid case_boot_sensor_irq_restart(uint32_t x){(void)x;}\nvoid case_boot_sensor_irq_final(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5f50)
for i in range(512):
 descriptor=bytearray(0xc0);hw=bytearray(0x100)
 struct.pack_into('<I',descriptor,0,0x40010000)
 struct.pack_into('<I',descriptor,108,0 if i%4 else 1)
 struct.pack_into('<H',descriptor,92,20);struct.pack_into('<H',descriptor,94,4)
 # Cover each error source, clean paths, transfer and auxiliary flags.
 enable=[0,1,2,4,8,0x800,0x20,0x80,0x100000,0x1000000,0x800000,0x41,0x80f][i%13]
 status=[0,0x100,0x20,0x4000000,0x80,0x40,0x40000000,0x80000000,0x10][i%9]
 control=[0,1,0x40,0x10000000,0x40000000,0x400000,0x10000001][i%7]
 if i>=256:
  enable=rng.choice([0,1,2,4,8,0x800,0x20,0x80f])
  status=rng.choice([0,0x100,0x20,0x4000000,0x80,0x40,0x100,0x120])
  control=rng.choice([0,1,0x40,0x10000000,0x10000001])
  struct.pack_into('<I',descriptor,144,rng.choice([0,1,4,32]))
 struct.pack_into('<I',hw,0,status);struct.pack_into('<I',hw,8,control);struct.pack_into('<I',hw,28,enable)
 struct.pack_into('<I',descriptor,144,0)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40010000,0x1000)
  u.mem_write(0x20000e24,bytes(descriptor));u.mem_write(0x40010000,bytes(hw))
  u.reg_write(UC_ARM_REG_R0,0x20000e24);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x080086f4:'error',0x080048e6:'ready',0x0800487a:'restart',0x08006776:'final'} if native else {sym['case_boot_sensor_irq_error']&~1:'error',sym['case_boot_sensor_irq_restart_ready']&~1:'ready',sym['case_boot_sensor_irq_restart']&~1:'restart',sym['case_boot_sensor_irq_final']&~1:'final'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0)))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08005f50 if native else sym['case_irq_child_5f50'])|1,0x20008000,count=1500)
  pair.append((calls,bytes(u.mem_read(0x20000e24,0xc0)),bytes(u.mem_read(0x40010000,0x40))))
 assert pair[0]==pair[1],(i,hex(enable),hex(status),hex(control),pair[0][0],pair[1][0],[(hex(j),a,b) for j,(a,b) in enumerate(zip(pair[0][1]+pair[0][2],pair[1][1]+pair[1][2])) if a!=b][:10])
print('PASS_CASE_SENSOR_IRQ_5F50',512)
