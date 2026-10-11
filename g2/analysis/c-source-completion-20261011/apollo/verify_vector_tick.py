#!/usr/bin/env python3
"""Bounded stock/source SysTick entry comparison under a tick-child cut."""
import hashlib,json,pathlib,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=pathlib.Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
HASH='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
STOCK=0x41b428;STOP=0x600000

def elf_parts(path):
 with open(path,'rb') as f:
  e=ELFFile(f); parts=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD' and s.data()]
  names={}
  for sec in e.iter_sections():
   if sec.header.sh_type=='SHT_SYMTAB':names.update({s.name:s['st_value'] for s in sec.iter_symbols()})
  return parts,names

def run(blob,parts,entry,cut,basepri,tick,source):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 for a,s in ((0x400000,0x50000),(0x500000,0x10000),(0x600000,0x1000),(0x20000000,0x30000),(0xe000e000,0x2000)):
  u.mem_map(a,s)
 u.mem_write(0x410000,blob)
 for a,d in parts:
  if 0x500000<=a<0x510000:u.mem_write(a,d)
 u.reg_write(A.UC_ARM_REG_SP,0x2002f000);u.reg_write(A.UC_ARM_REG_LR,STOP|1)
 u.reg_write(A.UC_ARM_REG_XPSR,0x01000000);u.reg_write(A.UC_ARM_REG_BASEPRI,basepri)
 done=[];seen=set();calls=[]
 def hook(cpu,pc,size,_):
  if pc==STOP:done.append(True);cpu.emu_stop()
  elif not source and pc==0x41b2f8:
   previous=cpu.reg_read(A.UC_ARM_REG_BASEPRI)
   cpu.reg_write(A.UC_ARM_REG_BASEPRI,48)
   cpu.reg_write(A.UC_ARM_REG_R0,previous)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  elif not source and pc==0x41b30e:
   cpu.reg_write(A.UC_ARM_REG_BASEPRI,cpu.reg_read(A.UC_ARM_REG_R0))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  elif source and pc==(entry&~1)+2:
   cpu.reg_write(A.UC_ARM_REG_R4,cpu.reg_read(A.UC_ARM_REG_BASEPRI))
   cpu.reg_write(A.UC_ARM_REG_PC,(pc+4)|1)
  elif source and pc==(entry&~1)+8:
   cpu.reg_write(A.UC_ARM_REG_BASEPRI,cpu.reg_read(A.UC_ARM_REG_R0))
   cpu.reg_write(A.UC_ARM_REG_PC,(pc+4)|1)
  elif source and pc==(entry&~1)+34:
   cpu.reg_write(A.UC_ARM_REG_BASEPRI,cpu.reg_read(A.UC_ARM_REG_R4))
   cpu.reg_write(A.UC_ARM_REG_PC,(pc+4)|1)
  elif pc==cut:
   calls.append((cpu.reg_read(A.UC_ARM_REG_BASEPRI),cpu.reg_read(A.UC_ARM_REG_SP)))
   cpu.reg_write(A.UC_ARM_REG_R0,tick);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  elif not source and STOCK<=pc<0x41b442:seen.update(range(pc,pc+size))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start(entry|1,STOP+2,count=100000)
 except Exception as exc:raise RuntimeError((hex(entry),hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
 assert done,(hex(entry),hex(u.reg_read(A.UC_ARM_REG_PC)))
 return (u.reg_read(A.UC_ARM_REG_BASEPRI),bytes(u.mem_read(0xe000ed04,4)),len(calls)),seen

def main():
 blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==HASH
 path=pathlib.Path(sys.argv[1]);parts,names=elf_parts(path);seen=set();cases=[]
 for mask in (0,16,48):
  for tick in (0,1):
   stock,s=run(blob,parts,STOCK,0x418408,mask,tick,False)
   candidate,_=run(blob,parts,names['opencfw_boot_systick_entry'],names['opencfw_bl_tick_increment']&~1,mask,tick,True)
   assert stock==candidate,(mask,tick,stock,candidate)
   seen|=s;cases.append({'initial_basepri':mask,'tick_result':tick})
 out={'status':'PASS','original_sha256':HASH,'source_elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'cases':cases,'stock_entry_bytes_visited':len(seen),
      'limits':['Runs source Cortex-M33 recompilation and locked stock under Unicorn, not selected M55 object.',
                'Stock BASEPRI save/restore helpers and source MRS/MSR instructions are controlled because Unicorn rejects this M-profile instruction path; this compares outer entry behavior only.',
                'Tick increment child is controlled; scheduler state changes and hardware interrupt delivery are outside scope.']}
 pathlib.Path(__file__).with_name('vector-tick-oracle-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
