#!/usr/bin/env python3
"""Bounded native/source CASE 0xba44..bb2c GPIO wrapper comparisons."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_gpio_compat_helpers_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
entries={0xa39c:'case_boot_gpio_a4_read',0xa3ac:'case_boot_gpio_b8_read',0xba44:'case_boot_gpio_a4_input',0xba64:'case_boot_gpio_b8_input',0xba84:'case_boot_gpio_a4_output',0xbaa4:'case_boot_gpio_b8_output',0xbac4:'case_boot_gpio_a4_high',0xbad8:'case_boot_gpio_b8_high',0xbae8:'case_boot_gpio_a4_low',0xbafc:'case_boot_gpio_b8_low',0xbb0c:'case_boot_gpio_a4_alt',0xbb2c:'case_boot_gpio_b8_alt'}
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'st.c';st.write_text('#include <stdint.h>\nvoid case_bus_gpio_config(uint32_t a,volatile uint32_t *b){(void)a;(void)b;}\nvoid case_control_write(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nuint32_t case_init_pin_read(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n');so=d/'t.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 native={0x08004d30:'config',0x08004e9e:'write',0x08004e94:'read'};source={sym['case_bus_gpio_config']&~1:'config',sym['case_control_write']&~1:'write',sym['case_init_pin_read']&~1:'read'}
 for offset,name in entries.items():
  for i in range(32):
   pairs=[]
   for original in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000014,struct.pack('<III',i,i%3,(i//3)%3));u.mem_write(0x200000a0,struct.pack('<III',i+2,(i+1)%3,(i//2)%3));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
    calls=[];targets=native if original else source
    def hook(uc,a,n,_):
     kind=targets.get(a)
     if kind is None:return
     x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2)
     calls.append((kind,x,y,z if kind=='write' else None));uc.reg_write(UC_ARM_REG_R0,i&1 if kind=='read' else x);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000000+offset if original else sym[name])|1,0x20008000,count=1000)
    pairs.append((bytes(u.mem_read(0x20000014,12)),bytes(u.mem_read(0x200000a0,12)),calls,u.reg_read(UC_ARM_REG_R0) if offset in (0xa39c,0xa3ac) else None))
   assert pairs[0]==pairs[1],(hex(offset),i,pairs)
 print('PASS_CASE_GPIO_COMPAT_HELPERS',len(entries)*32)
