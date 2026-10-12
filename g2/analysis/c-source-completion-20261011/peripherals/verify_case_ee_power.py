"""Actual Cortex-M0 CASE PMIC stop request retry comparison."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'components/case/legacy_default_candidate_20261010/shipmode_power_stop.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nuint32_t case_legacy_pmic_set(uint32_t a,uint32_t b){return 0;}\nuint32_t case_legacy_ee_first(uint32_t a,uint32_t*b,uint32_t c){return 0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,case_legacy_ee_power_stop',str(S),str(p),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
 for mode,success_at in itertools.product((0,1,0xffffffff),(0,1,2,3)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,B);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   cuts={(syms['case_legacy_pmic_set']&~1) if is_c else 0x080039e4:'pmic',(syms['case_legacy_ee_first']&~1) if is_c else 0x080035d4:'read'};events=[];reads=[0]
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if not k:return
    if k=='pmic':events.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    else:
     p=uc.reg_read(UC_ARM_REG_R1);events.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)))
     reads[0]+=1
     value=(9 if mode else 8) if reads[0]>success_at else 0xff
     uc.mem_write(p,bytes([value]));
    uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,mode)
   u.emu_start((syms['case_legacy_ee_power_stop'] if is_c else 0x08002c30)|1,0x20001000,count=10000)
   results.append((u.reg_read(UC_ARM_REG_R0),events))
  assert results[0]==results[1],(mode,success_at,results)
  print('PASS',mode,success_at,results[0])
