#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/initializer_log_alias.c';caller=R/'g2/components/bootloader/initializer_callbacks/initializer_callbacks.c'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'initializer-log-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_init_callback_redirect','-Wl,--gc-sections','-Wl,--defsym=opencfw_boot_elog_output=0x10020001','-Wl,--defsym=opencfw_bl_mutex_create=0x10030001',str(alias),str(caller),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_boot_init_callback_redirect');segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,returns,sp):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10000001)
 events=[];idx=[0]
 def cstr(p):
  out=[]
  for i in range(256):
   b=u.mem_read(p+i,1)[0]
   if not b:break
   out.append(b)
  return bytes(out).decode('ascii')
 def hook(emu,pc,size,data):
  if pc in (0x416610,0x10030000):
   events.append(('mutex',emu.reg_read(UC_ARM_REG_R0)));emu.reg_write(UC_ARM_REG_R0,returns[idx[0]]);idx[0]+=1;emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc in (0x4176ce,0x10020000):
   r=[emu.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];stack=emu.reg_read(UC_ARM_REG_SP);line,fmt=struct.unpack('<II',emu.mem_read(stack,8))
   events.append(('log',r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,cstr(fmt)))
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entry if source else 0x415590)|1,0x10000000,count=10000)
 return dict(events=events,ret=u.reg_read(UC_ARM_REG_R0),redirect=struct.unpack('<I',u.mem_read(0x2002712c,4))[0],protection=struct.unpack('<I',u.mem_read(0x20027130,4))[0])
cases=[]
for returns in itertools.product((0,0x51,0xffffffff),repeat=2):
 for sp in (0x2003eff0,0x2002fff0):
  a,b=run(False,returns,sp),run(True,returns,sp)
  assert a==b,(returns,sp,a,b)
  cases.append((returns,sp))
receipt=dict(status='PASS',cases=len(cases),stock_body_sha256=hashlib.sha256(blob[0x415590-0x410000:0x4155e8-0x410000]).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),caller_sha256=hashlib.sha256(caller.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Redirect initializer public entry, controlled mutex-create lower returns; semantic logger args, RAM, and return compared. Logger body/output, other initializer callers, and product data placement remain open. Scalar Cortex-M4 execution; M55 archive compile separate.')
(H/'initializer-log-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS initializer log alias',len(cases))
