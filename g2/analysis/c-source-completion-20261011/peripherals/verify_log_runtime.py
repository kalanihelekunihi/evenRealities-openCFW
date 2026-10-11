#!/usr/bin/env python3
"""Bounded register and fatal-reset prefix oracle for extended-log helpers."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/runtime.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-runtime-m4.o';ELF=OUT/'log-runtime-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def machine(stock=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in [(0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x10000),(0x20000000,0x1000),(0xe000e000,0x2000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in seg:u.mem_write(base,data)
 u.reg_write(A.UC_ARM_REG_SP,0x20000800);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 return u
rows=[]
for ipsr in (0,1,3,15,255,511):
 for control in (0,1,2,3):
  u=machine();u.reg_write(A.UC_ARM_REG_IPSR,ipsr);u.reg_write(A.UC_ARM_REG_CONTROL,control)
  u.emu_start(sy['g2_log_is_privileged']|1,0x100f00,count=30)
  privileged=u.reg_read(A.UC_ARM_REG_R0)
  u.reg_write(A.UC_ARM_REG_LR,0x100f01)
  u.emu_start(sy['g2_log_exception_number']|1,0x100f00,count=30)
  number=u.reg_read(A.UC_ARM_REG_R0)
  expected=int(ipsr!=0 or not(control&1))
  assert privileged==expected and (number&0x1ff)==ipsr&0x1ff
  assert (number&0x1ff if privileged else 0)==(ipsr&0x1ff)
  rows.append({'ipsr':ipsr,'control':control,'privileged':privileged,'exception':number})
# Stop at the first AIRCR write, before a real reset or the infinite idle loop.
fatal=[]
for initial in (0,0x700,0xffffffff,0x12345678):
 results=[]
 for stock in (True,False):
  u=machine(stock);u.mem_write(0xe000ed0c,struct.pack('<I',initial));writes=[]
  def write(cpu,access,addr,size,value,user):
   if addr==0xe000ed0c:writes.append([addr,size,value]);cpu.emu_stop()
  u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x44ab24 if stock else sy['g2_log_fatal_idle'])|1,0,count=30)
  assert len(writes)==1
  results.append(writes[0])
 assert results[0]==results[1]
 fatal.append({'initial':initial,'write':results[0]})
receipt={'status':'PASS_REGISTER_AND_FATAL_PREFIX','register_cases':len(rows),'fatal_cases':len(fatal),'register_rows':rows,'fatal_rows':fatal,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'limits':'Register helper is an architectural projection of outer MRS IPSR, not a same-entry stock helper. Fatal comparison stops at AIRCR write; no reset or infinite loop executed.'}
(OUT/'log-runtime-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(rows),len(fatal))
