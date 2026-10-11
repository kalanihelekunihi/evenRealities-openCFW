#!/usr/bin/env python3
"""Compare stock/source secondary read and write call traces at serial lowers."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/sensor_secondary_transport_candidate.c';obj=HERE/'sensor_secondary_transport_candidate.o';elf=HERE/'sensor_secondary_transport_candidate.elf';ld=HERE/'sensor_secondary_transport_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_binary_sensor_start','case_binary_sensor_byte_output','case_binary_sensor_ack','case_binary_sensor_byte_input','case_binary_sensor_final_pulse','case_binary_sensor_interbyte_pulse','case_binary_sensor_stop']
stock=[0x0800a4b4,0x0800a46c,0x0800a4fa,0x0800a436,0x0800a414,0x0800a3d2,0x0800a4dc]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
cases=[('case_legacy_ee_transport',n,fail) for n,fail in itertools.product([0,1,2,3],[0,1,2,3])]
cases += [('case_legacy_pmic_transport',0,fail) for fail in [0,1,2,3,4,199,200]]
for name,count,fail_at in cases:
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000114,b'\x7f');u.mem_write(0x20003000,b'\xee'*8)
  vals=[0x16,0x20003000,count] if name=='case_legacy_ee_transport' else [0x16,8,count]
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],vals):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];acks=[0];inputs=[0]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   calls.append((i,uc.reg_read(UC_ARM_REG_R0) if i==1 else None))
   if i==2:
    val=1 if acks[0]<fail_at else 0;acks[0]+=1
   elif i==3:val=0x50+inputs[0];inputs[0]+=1
   else:val=0xdeadbeef
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=0x0800292c if name=='case_legacy_ee_transport' else 0x08002a00
  u.emu_start((entry if original else sym[name])|1,0x20001000,count=50000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(0x20003000,8)),bytes(u.mem_read(0x20000114,1)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(name,count,fail_at,pair)
print('PASS_SECONDARY_TRANSPORT',len(cases))
