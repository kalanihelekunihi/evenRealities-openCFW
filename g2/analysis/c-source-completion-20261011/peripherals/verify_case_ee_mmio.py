"""Actual Cortex-M0 CASE standby MMIO child comparisons."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'components/case/legacy_default_candidate_20261010/shipmode_mmio_children.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,case_legacy_ee_wake_prepare',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
 entries={'prepare':('case_legacy_ee_wake_prepare',0x08005094),'enable':('case_legacy_ee_wake_enable',0x080050a8),'standby':('case_legacy_ee_enter_standby',0x080050c4)}
 for kind,mode,seed in itertools.product(entries,(0,43,0x2020,0xffffffff),(0,0x12345678)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,B);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   for a in (0x40007000,0x40007008,0x4000700c,0xe000ed10):u.mem_write(a,seed.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,mode)
   u.emu_start((syms[entries[kind][0]] if is_c else entries[kind][1])|1,0x20001000,count=1000)
   results.append((u.reg_read(UC_ARM_REG_R0),tuple(int.from_bytes(u.mem_read(a,4),'little') for a in (0x40007000,0x40007008,0x4000700c,0xe000ed10))))
  assert results[0]==results[1],(kind,mode,seed,results)
  print('PASS',kind,hex(mode),hex(seed),results[0])
