#!/usr/bin/env python3
"""Compare five Terminal ABI adapters' argument forwarding with selected providers."""
import hashlib,itertools,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_object_abi_aliases_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-object-abi-aliases'
PAIRS=[('audio_lv_object_call_43ded4','audio_uart_page_43ded4',0x43ded4,2),('audio_lv_object_call_441488','audio_uart_display_audio_reset_441488',0x441488,3),('audio_lv_object_call_450500','audio_uart_lv_style_unlink_450500',0x450500,2),('audio_lv_object_release_44d7b8','audio_uart_page_delete_event_filter_44d7b8',0x44d7b8,1),('audio_lv_object_size_call_43f4c0','audio_uart_page_43f4c0',0x43f4c0,3)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'aliases-oracle.o';elf=OUT/'aliases-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={provider}=0x{address|1:x}' for _,provider,address,_ in PAIRS],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for alias,provider,address,arity in PAIRS:
  for values in itertools.product((0,0x20001000,0xffffffff),(0,1,0xff),(0,0x240,0xffffffff)):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x100000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.mem_map(0x400000,0x100000);u.mem_map(0x20000000,0x100000);trace=[]
   def hook(cpu,pc,size,_):
    if pc!=address:return
    trace.append(tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)[:arity]))
    cpu.reg_write(A.UC_ARM_REG_R0,0x12345678);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
   for reg,v in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),values):u.reg_write(reg,v)
   u.emu_start(sym[alias]|1,0x600000,count=100)
   if trace!=[values[:arity]]:raise RuntimeError((alias,values,trace))
   cases+=1
 result={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_OBJECT_ABI_ALIASES_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_elf_sha256':sha(elf),'cases':cases,'providers':[{'alias':a,'provider':p,'stock_address':hex(v)} for a,p,v,_ in PAIRS],'scope':'Five exact stock-address provider adapters with register argument forwarding','limits':['Provider behavior supported by their existing C receipts; final placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],cases,sha(path))
if __name__=='__main__':main()
