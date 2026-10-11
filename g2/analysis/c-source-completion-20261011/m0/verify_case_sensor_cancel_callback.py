#!/usr/bin/env python3
"""Compare indirect CASE 0x86e0 callback's RAM and return state with C."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_cancel_callback_candidate.c'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);stub=d/'stub.c';stub.write_text('void HAL_UART_ErrorCallback(void *p){(void)p;}\n')
 flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
 objs=[]
 for src in (S,stub):
  o=d/(src.stem+'.o');subprocess.run(flags+[str(src),'-o',str(o)],check=True);objs.append(o)
 e=d/'x.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objs],'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  seg=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x86e0)
 for i in range(128):
  descriptor=0x20001000+4*rng.randrange(0,128);state=0x20002000+4*rng.randrange(0,128)
  initial=bytes(rng.getrandbits(8) for _ in range(128));out=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_map(0x300000,0x1000)
   u.mem_write(state,initial);u.mem_write(descriptor+40,state.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,descriptor);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x300001)
   u.emu_start((0x080086e0 if native else sym['case_boot_sensor_cancel_callback'])|1,0x300000,count=100)
   out.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(state,128))))
  assert out[0]==out[1],(i,out)
 print('PASS_CASE_SENSOR_CANCEL_CALLBACK',128)
