#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent; R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/elog_entry_alias.c'
caller=R/'g2/components/bootloader/nor_init/nor_runtime.c'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip(); elf=H/'elog-entry-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_provider_41fe62','-Wl,--gc-sections','-Wl,--defsym=opencfw_boot_elog_output=0x10020001','-Wl,--defsym=opencfw_provider_416610=0x10030001',str(alias),str(caller),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f); entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_provider_41fe62')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,handle,acquire_result,stack):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,stack);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.mem_write(0x200270e0,struct.pack('<I',handle))
 seen=[];acquires=[]
 def cstr(p):
  out=[]
  for i in range(256):
   b=u.mem_read(p+i,1)[0]
   if not b:break
   out.append(b)
  return bytes(out).decode('ascii')
 def hook(emu,pc,size,data):
  if pc in (0x416610,0x10030000):
   acquires.append(bytes(emu.mem_read(emu.reg_read(UC_ARM_REG_R0),16)).hex())
   emu.reg_write(UC_ARM_REG_R0,acquire_result);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc in (0x4176ce,0x10020000):
   sp=emu.reg_read(UC_ARM_REG_SP);r=[emu.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   line,fmt=struct.unpack('<II',emu.mem_read(sp,8))
   seen.append(dict(level=r[0],tag=cstr(r[1]),file=cstr(r[2]),function=cstr(r[3]),line=line,format=cstr(fmt)))
   emu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entry if source else 0x41fe62)|1,0x10000000,count=2000)
 if not seen:assert (u.reg_read(UC_ARM_REG_PC)&~1)==0x10000000,hex(u.reg_read(UC_ARM_REG_PC))
 return dict(acquires=acquires,log=seen)
cases=[]
for handle in (0,0x20001000,0xffffffff):
 for result in (0,1,7):
  for sp in (0x2003eff0,0x2002fff0):
   a,b=run(False,handle,result,sp),run(True,handle,result,sp)
   assert a==b,(handle,result,sp,a,b)
   cases.append((handle,result,sp))
receipt=dict(status='PASS',cases=len(cases),logging_cases=sum(h==0 and r==0 for h,r,_ in cases),stock_body_sha256=hashlib.sha256(blob[0x41fe62-0x410000:0x41fe9c-0x410000]).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),caller_sha256=hashlib.sha256(caller.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='One selected NOR mutex-init caller tested through stock/source public entry, with synthetic mutex-create return and attribute bytes compared. Full EasyLogger body and other callsites not executed. Scalar Cortex-M4 oracle; M55 archive compilation separate.')
(H/'elog-entry-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS elog entry alias',len(cases))
