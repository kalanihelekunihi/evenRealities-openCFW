#!/usr/bin/env python3
"""Compare session-list index narrowing and event child against stock."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_session_list_small_children_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-list-show-5ed208'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'small-children-oracle.o';elf=OUT/'small-children-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_terminal_ui_event_5e5484=0x5e5485',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,kind,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,value)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc!=0x5e5484:return
   trace.append(tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)))
   cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  symbol='audio_terminal_session_index_i16_5eca44' if kind=='index' else 'audio_terminal_session_list_event_5ed1fa'
  native=0x5eca44 if kind=='index' else 0x5ed1fa
  u.emu_start((sym[symbol] if compiled else native)|1,0x600000,count=60)
  return trace,u.reg_read(A.UC_ARM_REG_R0) if kind=='index' else None
 values=(0,1,32767,32768,65535,65536,0x12348001,0xffffffff)
 for i,value in enumerate(values):
  for kind in ('index','event'):
   stock=run(False,kind,value);source=run(True,kind,value)
   if stock!=source:print('mismatch',i,kind,value,stock,source);raise RuntimeError('session-list child mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SMALL_CHILDREN_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(values)*2,'scope':'Signed 16-bit index narrowing and fixed event 2/0/0 forwarding','limits':['Event lower effects remain isolated; final image/hardware remain open.']}
 p=OUT/'children-oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(values)*2,sha(p))
if __name__=='__main__':main()
