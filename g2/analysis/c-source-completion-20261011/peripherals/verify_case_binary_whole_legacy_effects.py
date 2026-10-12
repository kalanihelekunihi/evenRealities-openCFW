"""Connected CASE binary 06/41 through full legacy EE/FF control children."""
from pathlib import Path
import itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
E=Path(__file__).with_name('case-binary-whole.elf')
with E.open('rb') as f:
 elf=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
pairs={'ack':('case_binary_ack0641',0x080068d0),'log':('case_legacy_logger',0x08009170),'first':('case_legacy_ee_first',0x080035d4),'watchdog':('case_legacy_watchdog_set',0x08002c8e),'power':('case_legacy_ee_power_stop',0x08002c30),'prepare':('case_legacy_ee_wake_prepare',0x08005094),'enable':('case_legacy_ee_wake_enable',0x080050a8),'standby':('case_legacy_ee_enter_standby',0x080050c4),'reset':('case_legacy_reset_first',0x0800502c)}
def readz(u,p):
 v=bytearray()
 for i in range(80):
  c=u.mem_read(p+i,1)[0]
  if not c:break
  v.append(c)
 return bytes(v)
for op,usb,flag,n in itertools.product((6,0x41),(0,1),(0,1,0x7f),(0,20)):
 results=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,B);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(0x20004000,bytes([op,0,2,0,0])+bytes(251));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087f,bytes([usb]))
  cuts={(syms[c]&~1) if is_c else a:k for k,(c,a) in pairs.items()};events=[];writes=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   v=uc.reg_read(UC_ARM_REG_R0)
   if k=='log':events.append((k,readz(uc,v)))
   elif k=='first':events.append((k,v,uc.reg_read(UC_ARM_REG_R2)))
   elif k in ('standby','reset'):events.append((k,))
   else:events.append((k,v))
   uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def whook(uc,access,a,size,v,_):
   if 0x40007000<=a<0x40008000:writes.append((a,size,v))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,whook)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,0)
  u.emu_start((syms['case_binary_command_candidate'] if is_c else 0x08000e1c)|1,0x20001000,count=20000)
  results.append((u.reg_read(UC_ARM_REG_R0),events,writes))
 assert results[0]==results[1],(op,usb,flag,n,results)
 print('PASS',op,usb,flag,n,len(results[0][1]),results[0][2])
