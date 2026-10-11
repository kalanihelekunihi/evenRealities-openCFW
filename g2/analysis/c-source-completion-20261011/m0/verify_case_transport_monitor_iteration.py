#!/usr/bin/env python3
"""Bounded stock/C one-iteration oracle for CASE worker 0x82ec."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_monitor_candidate.c'
obj=H/'transport_monitor.oracle.o';stub=H/'transport_monitor.oracle_stub.c';stubobj=H/'transport_monitor.oracle_stub.o';elf=H/'transport_monitor.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nint32_t case_policy_sensor_delay(uint32_t x){return (int32_t)x;}\nvoid case_boot_transport_action(uint32_t x,uint32_t y){(void)x;(void)y;}\nuint32_t case_policy_log(uint32_t x){return x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x82ec)
for i in range(192):
 state=bytearray(0x60);shared=bytearray(0x20)
 state[16]=rng.randrange(2);state[17]=rng.randrange(2);state[0x30]=rng.randrange(2);state[0x4c]=rng.randrange(2)
 shared[1]=rng.choice([0,1,2,3,127,128,255]);shared[4]=rng.randrange(2);shared[7]=rng.randrange(2)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000b8,bytes(shared));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800a7b0:'delay',0x08001c1c:'action',0x08009170:'log'} if native else {sym['case_policy_sensor_delay']&~1:'delay',sym['case_boot_transport_action']&~1:'action',sym['case_policy_log']&~1:'log'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);calls.append((kind,x,y if kind=='action' else None))
   if kind=='delay' and x in (20,100):uc.emu_stop();return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080082ec if native else sym['case_boot_transport_cb_82ec'])|1,0x20008000,count=3000)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x20)),bytes(u.mem_read(0x2000087c,0x60))))
 assert pair[0]==pair[1],(i,list(state),list(shared),pair[0][:1],pair[1][:1])
print('PASS_CASE_TRANSPORT_MONITOR_ITERATION',192)
