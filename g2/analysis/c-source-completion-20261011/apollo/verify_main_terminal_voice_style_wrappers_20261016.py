#!/usr/bin/env python3
"""Compare voice page LVGL wrappers with pinned stock call ABI."""
import hashlib,itertools,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_style_wrappers_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-style-wrappers'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
TARGETS={'audio_uart_page_4411aa':0x4411aa,'audio_uart_page_4411e4':0x4411e4,'audio_uart_page_44132a':0x44132a,'audio_uart_page_441270':0x441270,'audio_terminal_ui_margins_5ebc5c':0x5ebc5c}
LOWER={'audio_uart_page_style_apply_44be4c':0x44be4c,'audio_uart_page_44122a':0x44122a,'audio_uart_page_441238':0x441238,'audio_uart_page_44120e':0x44120e,'audio_uart_page_44121c':0x44121c}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v|1:x}' for k,v in LOWER.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,name,object,value,selector):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,x in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),(object,value,selector)):u.reg_write(reg,x)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc not in LOWER.values():return
   n=next(k for k,v in LOWER.items() if v==pc)
   trace.append((n,tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)[:(4 if pc==0x44be4c else 3)])))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym[name] if compiled else TARGETS[name])|1,0x600000,count=100)
  return trace
 cases=list(itertools.product(TARGETS,(0,0x20080000),(0,0x50,0xd8,0xffffffff),(0,0xffffffff)))
 for i,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:raise RuntimeError(f'case {i} {args}: {a=} {b=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_STYLE_WRAPPERS_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Four LVGL style property IDs, byte truncation and four-side margin order','limits':['Underlying LVGL property mutation isolated.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
