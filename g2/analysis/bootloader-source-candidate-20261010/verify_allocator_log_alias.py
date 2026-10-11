#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent; R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/allocator_log_alias.c'
native=R/'g2/components/bootloader/log_call_adapters/log_adapters.c'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip(); elf=H/'allocator-log-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_allocator_log','-Wl,--gc-sections','-Wl,--defsym=opencfw_boot_elog_output=0x10020001',str(alias),str(native),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f); entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_boot_allocator_log')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,stack):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,stack);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.reg_write(UC_ARM_REG_R0,19)
 seen=[]
 def cstr(p):
  out=[]
  for i in range(256):
   b=u.mem_read(p+i,1)[0]
   if not b:break
   out.append(b)
  return bytes(out).decode('ascii')
 def hook(emu,pc,size,data):
  if pc in (0x4176ce,0x10020000):
   sp=emu.reg_read(UC_ARM_REG_SP)
   r=[emu.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   line,fmt=struct.unpack('<II',emu.mem_read(sp,8))
   seen.append(dict(level=r[0],tag=cstr(r[1]),file=cstr(r[2]),function=cstr(r[3]),line=line,format=cstr(fmt)))
   emu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entry if source else 0x41fd90)|1,0,count=1000)
 assert len(seen)==1, (source,seen,hex(u.reg_read(UC_ARM_REG_PC)))
 return seen[0]
cases=[]
for sp in (0x2003efc0,0x2003eff0,0x2002ffd0,0x20010000):
 a,b=run(False,sp),run(True,sp)
 assert a==b,(sp,a,b)
 cases.append(hex(sp))
receipt=dict(status='PASS',cases=len(cases),stacks=cases,metadata=run(True,0x2003eff0),image_sha256=hashlib.sha256(blob).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Original allocator call prefix begins at 0x41fd90 after unrelated TLSF setup. Stop at original/source elog entry and compare six semantic arguments; logger body and output are not covered. Only source caller line 19 is admitted. Scalar Cortex-M4 execution; M55 archive compilation separate.')
(H/'allocator-log-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS allocator log alias',len(cases))
