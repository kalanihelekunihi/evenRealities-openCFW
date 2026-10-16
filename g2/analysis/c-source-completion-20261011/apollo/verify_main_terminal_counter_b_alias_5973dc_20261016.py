#!/usr/bin/env python3
"""Check stock 0x5973dc and C adapter against the same owned RAM word."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_counter_b_alias_5973dc.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-counter-b-alias-5973dc'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ADDR=0x20119284
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_td_counter_b_get=0x300001',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x300000,0x1000);u.mem_map(0x20000000,0x200000);u.mem_write(ADDR,struct.pack('<I',value));trace=[]
  def hook(cpu,pc,size,_):
   if pc!=0x300000:return
   trace.append('owned_getter');cpu.reg_write(A.UC_ARM_REG_R0,struct.unpack('<I',cpu.mem_read(ADDR,4))[0]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=sym['audio_terminal_counter_b_get_5973dc'] if compiled else 0x5973dc
  u.emu_start(entry|1,0x600000,count=30)
  return u.reg_read(A.UC_ARM_REG_R0),trace
 cases=0
 for value in (0,1,0xff,0x100,0x12345678,0x80000000,0xffffffff):
  stock,st=run(False,value);candidate,ct=run(True,value)
  if stock!=candidate or stock!=value or st or ct!=['owned_getter']:raise RuntimeError((value,stock,candidate,st,ct))
  cases+=1
 result={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_COUNTER_B_ALIAS_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':cases,'stock_ram_address':hex(ADDR),'scope':'Stock direct RAM load equals existing source-owned getter via ABI adapter','limits':['Final RAM placement and runtime initialization remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],cases,sha(path))
if __name__=='__main__':main()
