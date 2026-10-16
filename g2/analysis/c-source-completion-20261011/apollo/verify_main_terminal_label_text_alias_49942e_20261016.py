#!/usr/bin/env python3
"""Check Terminal 0x49942e ABI forwarding to the existing stock-compared provider."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_label_text_alias_49942e.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-label-text-alias-49942e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'alias-oracle.o';elf=OUT/'alias-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_uart_page_49942e=0x49942f',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for label in (0,0x20001000,0x2000ffff,0xffffffff):
  for textptr in (0,0x20002000,0x20003000,0xffffffff):
   for result in (0,0x12345678,0xffffffff):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x100000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    u.mem_map(0x400000,0x100000);u.mem_map(0x20000000,0x100000)
    trace=[]
    def hook(cpu,pc,size,_):
     if pc==0x49942e:
      trace.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
      cpu.reg_write(A.UC_ARM_REG_R0,result);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,label);u.reg_write(A.UC_ARM_REG_R1,textptr)
    u.emu_start(sym['audio_lv_anim_start_49942e']|1,0x600000,count=100)
    if trace!=[(label,textptr)]:raise RuntimeError((label,textptr,result,trace))
    cases+=1
 result={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_ALIAS_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_elf_sha256':sha(elf),'cases':cases,'scope':'Exact argument forwarding to existing 0x49942e C provider; provider behavior established by its separate stock oracle','limits':['Final image placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],cases,sha(path))
if __name__=='__main__':main()
