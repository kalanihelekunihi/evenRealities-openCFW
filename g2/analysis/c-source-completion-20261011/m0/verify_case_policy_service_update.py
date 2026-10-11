#!/usr/bin/env python3
"""Bounded native/source call and RAM comparison for CASE 0xce34."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_service_update_candidate.c'
obj=H/'application_policy_service_update.oracle.o';stub=H/'application_policy_service_update.oracle_stub.c';stub_obj=H/'application_policy_service_update.oracle_stub.o';elf=H/'application_policy_service_update.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_policy_sensor_command','case_policy_sensor_delay','case_policy_sensor_sample','case_policy_sensor_divide','case_policy_sensor_prepare','case_policy_idle_clear','case_policy_log']
stub.write_text('#include <stdint.h>\n'+'\n'.join(('uint32_t '+n+'(void){return 0;}' if n.endswith(('sample','divide')) else ('void '+n+'(uint32_t a,uint32_t b){(void)a;(void)b;}' if n.endswith('command') or n.endswith('divide') else 'void '+n+'(uint32_t a){(void)a;}' if n.endswith(('delay','log')) else 'void '+n+'(void){}')) for n in names)+'\n')
subprocess.run(flags+[str(stub),'-o',str(stub_obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stub_obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={0x080099e8:'command',0x0800a7b0:'delay',0x08002edc:'sample',0x08000160:'divide',0x0800d250:'prepare',0x08009a14:'clear',0x08009170:'log'}
source={sym[n]&~1:k for n,k in zip(names,['command','delay','sample','divide','prepare','clear','log'])}
rng=random.Random(0xce34);checked=0
for mode in range(8):
 for i in range(16):
  state=bytearray(rng.randrange(256) for _ in range(0x68));state[0x10]=int(bool(mode&1));state[0x11]=int(bool(mode&2));state[0x31]=int(bool(mode&4));state[0x4d]=int(bool(mode&4));state[0x33]=0;state[0x4f]=0
  vars=bytearray(rng.randrange(256) for _ in range(0x100));vars[0x7c]=i%8;vars[0x7d]=(i+1)%8;vars[0xbf]=i&1
  guard=i&1; divisor=1+(i%10)
  sample_values=[(i*53+j*207)%900 for j in range(12)]
  divide_values=[(i*31+j*67)%170 for j in range(4)]
  pair=[]
  for is_native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x20000000,bytes(vars));u.mem_write(0x20000105,bytes([guard,divisor]))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   trace=[]
   def hook(uc,addr,size,_):
    kind=(native if is_native else source).get(addr)
    if kind is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    trace.append((kind,r0,r1) if kind in ('command','divide') else (kind,r0) if kind in ('delay','log') else (kind,))
    if kind=='sample':
     idx=sum(1 for item in trace if item[0]=='sample')-1;uc.reg_write(UC_ARM_REG_R0,sample_values[idx])
    elif kind=='divide':
     idx=sum(1 for item in trace if item[0]=='divide')-1;uc.reg_write(UC_ARM_REG_R0,divide_values[idx])
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=0x0800ce34 if is_native else sym['case_policy_service_update']
   u.emu_start(entry|1,0x20001000,count=10000)
   pair.append((bytes(u.mem_read(0x2000087c,0x68)),bytes(u.mem_read(0x2000007c,2)),trace))
  assert pair[0]==pair[1],(mode,i,pair[0][2],pair[1][2],pair[0][:2],pair[1][:2])
  checked+=1
print('PASS_CASE_POLICY_SERVICE_UPDATE',checked)
