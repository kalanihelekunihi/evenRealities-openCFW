#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/update_log_alias.c';caller=R/'g2/components/bootloader/update_core/update_core.c'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'update-log-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_verify','-Wl,--gc-sections','-Wl,--defsym=opencfw_boot_elog_output=0x10020001','-Wl,--defsym=opencfw_boot_file_open=0x10030001','-Wl,--defsym=opencfw_boot_file_prepare=0x10030011','-Wl,--defsym=opencfw_boot_file_read=0x10030021','-Wl,--defsym=opencfw_boot_file_close=0x10030031',str(alias),str(caller),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_boot_verify')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
HANDLE=0x20001000;HEADER=0x20002000
def run(source,initial,sp):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.reg_write(UC_ARM_REG_R0,HANDLE);u.reg_write(UC_ARM_REG_R1,HEADER)
 u.mem_write(HANDLE,struct.pack('<I',initial));u.mem_write(HEADER,b'\0'*32)
 events=[]
 def cstr(p):
  out=[]
  for i in range(256):
   b=u.mem_read(p+i,1)[0]
   if not b:break
   out.append(b)
  return bytes(out).decode('ascii')
 def hook(emu,pc,size,data):
  if pc in (0x4153a4,0x10030000):
   events.append(('open',cstr(emu.reg_read(UC_ARM_REG_R0)),emu.reg_read(UC_ARM_REG_R1)))
   emu.reg_write(UC_ARM_REG_R0,0);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc in (0x4176ce,0x10020000):
   x=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   stack=emu.reg_read(UC_ARM_REG_SP);line,fmt,arg=struct.unpack('<III',emu.mem_read(stack,12))
   events.append(('log',x[0],cstr(x[1]),cstr(x[2]),cstr(x[3]),line,cstr(fmt),cstr(arg)))
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entry if source else 0x42d890)|1,0x10000000,count=10000)
 return dict(events=events,ret=u.reg_read(UC_ARM_REG_R0),handle=struct.unpack('<I',u.mem_read(HANDLE,4))[0])
cases=[]
for initial in (0,0x51,0xffffffff):
 for sp in (0x2003eff0,0x2002fff0):
  a,b=run(False,initial,sp),run(True,initial,sp)
  assert a==b,(initial,sp,a,b)
  cases.append((initial,sp))
receipt=dict(status='PASS',cases=len(cases),image_sha256=hashlib.sha256(blob).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),caller_sha256=hashlib.sha256(caller.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Only verify open-failure path compared through public entry, with controlled open return zero and logger entry. Source update core retains stock data-address pointers for tag/file/function/format/path; product placement remains unresolved. No accepted-file verification or logger output proof.')
(H/'update-log-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS update log alias',len(cases))
