#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/dfu_log_alias.c';native=R/'g2/components/bootloader/log_call_adapters/log_adapters.c';task=R/'g2/components/bootloader/dfu_task/task.c'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'dfu-log-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_dfu_log','-Wl,--gc-sections','-Wl,--defsym=opencfw_boot_elog_output=0x10020001',str(alias),str(native),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,line,detail,sp):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,line);u.reg_write(UC_ARM_REG_R2,detail);u.reg_write(UC_ARM_REG_R5,0x433c54);u.reg_write(UC_ARM_REG_R6,0x4310c4);u.reg_write(UC_ARM_REG_R7,0x433fe0);u.reg_write(UC_ARM_REG_R8,0x4336e4);u.reg_write(UC_ARM_REG_R10,detail)
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
   r=[emu.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]; stack=emu.reg_read(UC_ARM_REG_SP)
   words=struct.unpack('<IIII',emu.mem_read(stack,16));out=dict(level=r[0],tag=cstr(r[1]),file=cstr(r[2]),function=cstr(r[3]),line=words[0],format=cstr(words[1]))
   if line==532:out.update(path=cstr(words[2]),detail=words[3])
   seen.append(out);emu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 start=(syms['opencfw_boot_dfu_log'] if line==356 else syms['opencfw_dfu_log_detail_native']) if source else (0x42dcb2 if line==356 else 0x42de7c)
 u.emu_start(start|1,0,count=1000)
 assert len(seen)==1,(source,line,hex(u.reg_read(UC_ARM_REG_PC)))
 return seen[0]
cases=[]
for line in (356,532):
 for detail in ((0,) if line==356 else (0,1,31,0xffffffff)):
  for sp in (0x2003eff0,0x2002fff0):
   a,b=run(False,line,detail,sp),run(True,line,detail,sp)
   assert a==b,(line,detail,sp,a,b)
   cases.append((line,detail,sp))
receipt=dict(status='PASS',cases=len(cases),fixed_alias_cases=sum(x[0]==356 for x in cases),read_detail_cases=sum(x[0]==532 for x in cases),image_sha256=hashlib.sha256(blob).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),task_sha256=hashlib.sha256(task.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Two bounded stock call prefixes compared at EasyLogger entry. Fixed line 356 exercises alias; line 532 exercises the selected detail adapter after caller repair. Other DFU lines have historical static callsite metadata but are not current executed fixtures. Logger body/output and full DFU task not proved.')
(H/'dfu-log-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS DFU log alias/detail',len(cases))
