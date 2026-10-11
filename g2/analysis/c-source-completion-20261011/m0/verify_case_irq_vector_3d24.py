#!/usr/bin/env python3
"""CASE 0x3d24 original/C hall vector branch and RAM oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_vector_3d24_candidate.c';obj=H/'irq_vector_3d24.oracle.o';stub=H/'irq_vector_3d24.oracle_stub.c';stubobj=H/'irq_vector_3d24.oracle_stub.o';elf=H/'irq_vector_3d24.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_legacy_logger(const char *s,...){(void)s;return 0;}\nvoid case_boot_irq_hall_prepare(uint32_t x){(void)x;}\nuint32_t case_boot_irq_hall_state(void){return 0;}\nint32_t case_boot_sensor_finish_signal(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nvoid case_boot_irq_clear(uint32_t m){(void)m;}\nvoid case_boot_button_mode_reset(uint32_t a){(void)a;}\nvoid case_init_boost_set(uint32_t a){(void)a;}\nvoid case_boot_usb_reset_gls_box(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3d24)
for i in range(128):
 state=bytearray(rng.randbytes(0x80));state[2]=i%3==0;state[8:12]=struct.pack('<I',i*3);state[49]=i%2;state[51]=i%4==0;state[77]=i%3;state[79]=i%5==0;state[56:58]=struct.pack('<H',i%4);state[84:86]=struct.pack('<H',i%5)
 bus=bytearray(rng.randbytes(0x40));bus[16:20]=struct.pack('<I',(rng.getrandbits(32)&~32)|(32 if i%2 else 0));hall=i%4==0;quiet=i%3==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000bf,bytes([quiet]));u.mem_write(0x200000f0,struct.pack('<I',0x20003500));u.mem_write(0x2000010c,struct.pack('<II',i*3-(i%8),i%3));u.mem_write(0x40021800,bytes(bus))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009170:'log',0x08003848:'prepare',0x08002a5c:'hall',0x0800a888:'notify',0x08004d04:'clear',0x08003a00:'mode',0x08002c30:'boost',0x08003656:'reset'} if native else {sym['case_legacy_logger']&~1:'log',sym['case_boot_irq_hall_prepare']&~1:'prepare',sym['case_boot_irq_hall_state']&~1:'hall',sym['case_boot_sensor_finish_signal']&~1:'notify',sym['case_boot_irq_clear']&~1:'clear',sym['case_boot_button_mode_reset']&~1:'mode',sym['case_init_boost_set']&~1:'boost',sym['case_boot_usb_reset_gls_box']&~1:'reset'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
   if kind=='log':calls.append((kind,bytes(uc.mem_read(r0,80)).split(b'\0',1)[0]))
   elif kind=='notify':calls.append((kind,r0,r1))
   elif kind in ('mode','boost'):calls.append((kind,r0))
   elif kind=='clear':calls.append((kind,r0))
   else:calls.append((kind,))
   uc.reg_write(UC_ARM_REG_R0,int(hall) if kind=='hall' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003d24 if native else sym['case_vector_irq_3d24'])|1,0x20008000,count=1000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x80)),bytes(u.mem_read(0x2000010c,8))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0],[(x,a,b) for x,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:8])
print('PASS_CASE_IRQ_VECTOR_3D24',128)
