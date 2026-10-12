"""CASE 0xee full native/C branch sequence with real lower ABI cuts."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'components/case/legacy_default_candidate_20261010/shipmode_ee_prefix.c'
shim='''#include <stdint.h>\nuint32_t case_legacy_logger(const char*a,...){return 0;}\nuint32_t case_legacy_ee_first(uint32_t a,uint32_t*b,uint32_t c){return 0;}\nuint32_t case_legacy_watchdog_set(uint32_t a){return 0;}\nuint32_t case_legacy_ee_power_stop(uint32_t a){return 0;}\nuint32_t case_legacy_ee_wake_prepare(uint32_t a){return 0;}\nuint32_t case_legacy_ee_wake_enable(uint32_t a){return 0;}\nuint32_t case_legacy_ee_enter_standby(void){return 0;}\n'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(shim);e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,case_legacy_ee_prefix',str(S),str(p),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
 pairs={'log':('case_legacy_logger',0x08009170),'first':('case_legacy_ee_first',0x080035d4),'watchdog':('case_legacy_watchdog_set',0x08002c8e),'power':('case_legacy_ee_power_stop',0x08002c30),'prepare':('case_legacy_ee_wake_prepare',0x08005094),'enable':('case_legacy_ee_wake_enable',0x080050a8),'standby':('case_legacy_ee_enter_standby',0x080050c4)}
 for flag,usb,ret in itertools.product((0,1),(0,1),(0,7)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,B);u.mem_map(0x00100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20004000,bytes([0xee,0x55])+bytes(30));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087f,bytes([usb]))
   cuts={(syms[c]&~1) if is_c else n:k for k,(c,n) in pairs.items()};calls=[];writes=[]
   def readz(uc,p):
    v=bytearray()
    for i in range(64):
     c=uc.mem_read(p+i,1)[0]
     if not c:break
     v.append(c)
    return bytes(v)
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None:return
    x=uc.reg_read(UC_ARM_REG_R0)
    if k=='log':calls.append((k,readz(uc,x)))
    elif k=='first':calls.append((k,x,uc.reg_read(UC_ARM_REG_R2)))
    elif k=='standby':calls.append((k,))
    else:calls.append((k,x))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def whook(uc,access,a,size,value,_):
    if 0x40007000<=a<0x40008000:writes.append((a,size,value))
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,whook)
   u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,2)
   u.emu_start((syms['case_legacy_ee_prefix'] if is_c else 0x08000928)|1,0x20001000,count=20000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,writes))
  assert results[0]==results[1],(flag,usb,ret,results)
  print('PASS',flag,usb,ret,len(results[0][1]),results[0][2])
