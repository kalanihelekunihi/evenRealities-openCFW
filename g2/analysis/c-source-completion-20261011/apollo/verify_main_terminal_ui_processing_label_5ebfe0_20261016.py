#!/usr/bin/env python3
"""Compare the bounded processing-label helper with stock Thumb code."""
import hashlib, json, struct, subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]; G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_processing_label_5ebfe0.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-processing-label-5ebfe0'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x2006e0d0; CALL=0x49942e
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN: raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True); obj=OUT/'oracle.o'; elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',f'--defsym=audio_terminal_ui_state_base=0x{STATE:x}',f'--defsym=audio_uart_page_49942e=0x{CALL|1:x}',str(obj),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f); seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']; symbol={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,label):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE+0x204,struct.pack('<I',label));u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc!=CALL:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   trace.append((r0,bytes(cpu.mem_read(r1,64)).split(b'\0',1)[0].decode()))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((symbol['audio_terminal_ui_processing_label_5ebfe0'] if compiled else 0x5ebfe0)|1,0x600000,count=100)
  return trace,bytes(u.mem_read(STATE+0x204,4))
 for label in (0,0x20080000,0x12345678,0xffffffff):
  stock=run(False,label);source=run(True,label)
  if stock!=source:raise RuntimeError(f'processing label mismatch {label:x} {stock!r} {source!r}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_PROCESSING_LABEL_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':4,'scope':'Null gate and exact label text/call target','limits':['Downstream LVGL label effects isolated; full main image/linker and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
