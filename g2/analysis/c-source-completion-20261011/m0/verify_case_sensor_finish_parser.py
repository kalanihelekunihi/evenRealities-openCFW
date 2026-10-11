#!/usr/bin/env python3
"""CASE 0x6544 native/source parser comparisons at physical child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_callback_finish_candidate.c';obj=H/'sensor_finish_parser.oracle.o';stub=H/'sensor_finish_parser.oracle_stub.c';stubobj=H/'sensor_finish_parser.oracle_stub.o';elf=H/'sensor_finish_parser.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_sensor_bind(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\nuint32_t case_boot_sensor_finish_guard(uint32_t a,const uint8_t *b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_boot_sensor_finish_probe(const uint8_t *a){(void)a;return 0;}\nvoid case_boot_sensor_finish_signal(uint32_t a,uint32_t b){(void)a;(void)b;}\nvoid case_boot_sensor_finish_reset(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x6544)
for i in range(192):
 state=bytearray(4);buffer=bytearray(rng.randbytes(1220));count=[0,1,2,3,4,5,6,20,60,61,1199,1200][i%12]
 byte=[ord('Z'),ord('D'),ord('d'),ord('X'),10][(i//12)%5];state[0]=byte;struct.pack_into('<H',state,2,count)
 buffer[0]=[ord('Z'),ord('D'),ord('d')][(i//3)%3];buffer[1]=0xa5 if i%4 else 0;buffer[2]=0x7f if i%2 else 0xcf;buffer[3]=i%17;buffer[4]=i%3
 probe=i%3;guard=3 if i%5==0 else 0;bind=i%4;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x200000f0,struct.pack('<I',0x20002000));u.mem_write(0x20000108,bytes(state));u.mem_write(0x20000974,bytes(buffer))
  u.mem_write(0x20003000,struct.pack('<I',0x40013800 if i%17 else 0x40004800))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  targets=({0x080064ec:'bind',0x080063ec:'guard',0x0800be74:'probe',0x0800a888:'signal',0x0800a358:'reset'} if native else {sym['case_boot_sensor_bind']&~1:'bind',sym['case_boot_sensor_finish_guard']&~1:'guard',sym['case_boot_sensor_finish_probe']&~1:'probe',sym['case_boot_sensor_finish_signal']&~1:'signal',sym['case_boot_sensor_finish_reset']&~1:'reset'})
  calls=[]
  def hook(uc,a,size,_):
   if a not in targets:return
   kind=targets[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
   item=(kind,r0,r1,r2) if kind=='bind' else (kind,r0,r1,r2,r3) if kind=='guard' else (kind,r0,bytes(uc.mem_read(r0,8))) if kind=='probe' else (kind,r0,r1) if kind=='signal' else (kind,)
   calls.append(item);uc.reg_write(UC_ARM_REG_R0,probe if kind=='probe' else guard if kind=='guard' else bind if kind=='bind' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08006544 if native else sym['case_boot_sensor_callback_finish'])|1,0x20008000,count=1500)
  pair.append((bytes(u.mem_read(0x20000108,4)),bytes(u.mem_read(0x20000974,1220)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_FINISH_PARSER',192)
