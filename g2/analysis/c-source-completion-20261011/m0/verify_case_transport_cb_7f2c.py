#!/usr/bin/env python3
"""CASE 0x7f2c native/source periodic power worker one-loop cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_cb_7f2c_candidate.c';obj=H/'cb7f2c.oracle.o';stub=H/'cb7f2c.oracle_stub.c';stubobj=H/'cb7f2c.oracle_stub.o';elf=H/'cb7f2c.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
undefined=[line.split()[-1] for line in subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
stub.write_text('#include <stdint.h>\n'+''.join(f'uint32_t {name}(void){{return 0;}}\n' for name in undefined))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={0x2a68:'case_boot_periodic_power_update',0x0160:'case_policy_sensor_divide',0x9ff0:'case_boot_temperature_sample',0x9f18:'case_boot_current_sample',0xa01e:'case_boot_battery_sample',0x9df4:'case_init_pmic_prepare',0x39c8:'case_init_pmic_write',0x9ebc:'case_boot_battery_percent',0x9170:'case_policy_log',0x39e4:'case_init_pmic_reset',0x35d4:'case_init_pmic_read',0x2c8e:'case_init_power_set',0x2c30:'case_init_boost_set',0x5094:'case_init_wake_mask',0x50a8:'case_init_wake_config',0x50c4:'case_init_wake_clock',0x12e4:'case_policy_box_failure_reset',0x6b80:'case_boot_transport_stop_clock',0x1334:'case_boot_aging_begin',0xa7b0:'case_policy_wait'}
rng=random.Random(0x7f2c)
for i in range(224):
 state=bytearray(rng.randbytes(128));shared=bytearray(0x120);state[1]=[0,99,50][i%3];state[3]=i%2;state[0x16]=i%2;state[0x19]=0;state[0x32]=[50,100][i%2];state[0x4e]=[50,100][(i//2)%2]
 struct.pack_into('<I',state,8,5*(i+1) if i%4 else 5*(i+1)+1);shared[0x3c]=i%7==0;shared[0x3d]=0;struct.pack_into('<I',shared,0x44,[0,7195,7200][i%3]);quiet=1
 temp=[0,200,399,400,450,451,500][i%7];current=123456 if i%19==0 else rng.randrange(3000);voltage=[3000,3250,4000][i%3];percent=99 if i%2 else 100;pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000b8,bytes(shared));u.mem_write(0x200000bf,bytes([quiet]));u.mem_map(0x40007000,0x1000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08000000+a:v for a,v in native.items()} if original else {sym[v]&~1:v for v in undefined});calls=[];stopped=[False]
  def hook(uc,a,n,_):
   name=targets.get(a)
   if name is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2)
   if name=='case_policy_wait' and x==1000:calls.append((name,x));stopped[0]=True;uc.emu_stop();return
   if name=='case_policy_sensor_divide':calls.append((name,x,y));uc.reg_write(UC_ARM_REG_R0,x//y);uc.reg_write(UC_ARM_REG_R1,x%y)
   elif name in ('case_boot_temperature_sample','case_boot_current_sample','case_boot_battery_sample','case_boot_battery_percent'):
    value={'case_boot_temperature_sample':temp,'case_boot_current_sample':current,'case_boot_battery_sample':voltage,'case_boot_battery_percent':percent}[name]
    calls.append((name,));uc.mem_write(x,struct.pack('<I',value))
   elif name=='case_init_pmic_read':calls.append((name,x,z));uc.mem_write(y,b'\0')
   elif name=='case_policy_log':calls.append((name,bytes(uc.mem_read(x,128)).split(b'\0')[0]))
   elif name in ('case_init_pmic_write','case_init_pmic_reset'):calls.append((name,x,y))
   else:calls.append((name,x if name in ('case_init_power_set','case_init_boost_set','case_init_wake_mask','case_init_wake_config','case_boot_transport_stop_clock','case_policy_wait') else None))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08007f2c if original else sym['case_boot_transport_cb_7f2c'])|1,0,count=10000)
  assert stopped[0],(i,original,calls)
  pair.append((calls,bytes(u.mem_read(0x2000087c,128)),bytes(u.mem_read(0x200000b8,0x120)),bytes(u.mem_read(0x40007018,4))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0])
print('PASS_CASE_TRANSPORT_CB_7F2C',224)
