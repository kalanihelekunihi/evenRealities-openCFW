#!/usr/bin/env python3
"""Compare Apollo label format assertion paths through their terminal fault write."""
import hashlib,json,struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT=G2/'build/c-firmware/20261016/main-label-fatal-paths'
FMT_ELF=G2/'build/c-firmware/20261016/main-terminal-label-text-fmt-49954c/oracle.elf'
VPRINTF_ELF=G2/'build/c-firmware/20261016/main-lv-label-vprintf-489ad2/oracle.elf'
SOURCES=(G2/'components/audio/uart_thread_source_candidate/terminal_label_text_fmt_49954c.c',G2/'components/audio/uart_thread_source_candidate/display_lv_label_vprintf_489ad2.c')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_elf(path):
 with path.open('rb') as f:
  e=ELFFile(f)
  return ([(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'],{s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()})
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 fo=json.loads((FMT_ELF.parent/'oracle-receipt.json').read_text());vo=json.loads((VPRINTF_ELF.parent/'oracle-receipt.json').read_text())
 if fo['oracle_elf_sha256']!=sha(FMT_ELF) or vo['oracle_elf_sha256']!=sha(VPRINTF_ELF) or fo['source_sha256']!=sha(SOURCES[0]) or vo['source_sha256']!=sha(SOURCES[1]):raise RuntimeError('base oracle evidence changed')
 def run(kind,compiled,mode,length):
  elf=FMT_ELF if kind=='label' else VPRINTF_ELF;seg,sym=load_elf(elf)
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for addr,data in seg:u.mem_write(addr,data)
  u.mem_map(0x20000000,0x100000);trace=[]
  def cstr(cpu,a):return bytes(cpu.mem_read(a,180)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   if pc not in (0x44d25c,0x483fea,0x44f718):return
   sp=cpu.reg_read(A.UC_ARM_REG_SP);r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if pc==0x44d25c:
    vals=struct.unpack('<III',cpu.mem_read(sp,12));trace.append(('log',r[0],cstr(cpu,r[1]),r[2],cstr(cpu,r[3]),*(cstr(cpu,x) for x in vals)));value=0
   elif pc==0x483fea:
    trace.append(('measure',r[0],r[1],r[2],r[3]));value=length
   elif pc==0x44f718:
    trace.append(('alloc',r[0]));value=0
   else:raise RuntimeError(f'unexpected lower {pc:x}')
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  def fault(cpu,access,address,size,value,_):trace.append(('fault_write',address,size,value));return False
  u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  if kind=='label':
   u.reg_write(A.UC_ARM_REG_R0,0 if mode=='null_object' else 0x20001000)
   u.reg_write(A.UC_ARM_REG_R1,0x20002000 if mode=='null_object' else 0)
   entry=sym['audio_lv_label_set_text_fmt_49954c'] if compiled else 0x49954c
  else:
   u.reg_write(A.UC_ARM_REG_R0,0x20002000);u.reg_write(A.UC_ARM_REG_R1,0x20003000)
   entry=sym['audio_uart_lv_label_vprintf_489ad2'] if compiled else 0x489ad2
  try:u.emu_start(entry|1,0x600000,count=250)
  except UcError:
   if not trace or trace[-1][0]!='fault_write':raise
  if not trace or trace[-1][0]!='fault_write':raise RuntimeError(f'no fault {kind} {mode} {trace}')
  return trace
 cases=[]
 for mode in ('null_object','null_format'):
  cases.append(('label',mode,0))
 for length in (0,13,0xffffffff):cases.append(('vprintf','allocation_failure',length))
 for kind,mode,length in cases:
  a,b=run(kind,False,mode,length),run(kind,True,mode,length)
  if a!=b:raise RuntimeError(f'assertion mismatch {kind} {mode} {length}: {a} != {b}')
 OUT.mkdir(parents=True,exist_ok=True)
 result={'status':'PASS_EXPERIMENTAL_MAIN_LABEL_FATAL_PATHS_ORACLE','cases':len(cases),'payload_sha256':PIN,'sources':[{ 'path':str(s.relative_to(ROOT)),'sha256':sha(s)} for s in SOURCES],'base_oracles':[str((FMT_ELF.parent/'oracle-receipt.json').relative_to(ROOT)),str((VPRINTF_ELF.parent/'oracle-receipt.json').relative_to(ROOT))],'scope':'Null object, null format and allocator failure log fields and terminal unmapped write','limits':['Physical fault/recovery response and real lower effects remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],len(cases),sha(path))
if __name__=='__main__':main()
