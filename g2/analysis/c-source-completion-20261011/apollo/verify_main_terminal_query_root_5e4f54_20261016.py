#!/usr/bin/env python3
"""Compare terminal query root/panel constructor against pinned stock."""
import hashlib,itertools,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_root_5e4f54.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-root-5e4f54'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS={'audio_uart_device_role_get':0x45a568,'audio_uart_page_43de82':0x43de82,'audio_uart_page_43f4c0':0x43f4c0,'audio_uart_page_43f6b8':0x43f6b8,'audio_uart_page_44104c':0x44104c,'audio_uart_page_44127e':0x44127e,'audio_uart_page_44129e':0x44129e,'audio_uart_page_44131c':0x44131c,'audio_uart_page_44146a':0x44146a,'audio_terminal_ui_theme_5e47cc':0x5e47cc,'audio_uart_page_43dfa4':0x43dfa4,'audio_uart_page_43f506':0x43f506,'audio_uart_page_4412ec':0x4412ec}
BY_ADDR={v:k for k,v in CALLS.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}=0x{a|1:x}' for n,a in CALLS.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,role,mode,parent):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,parent);u.reg_write(A.UC_ARM_REG_R1,mode)
  trace=[];created=0
  def hook(cpu,pc,size,_):
   nonlocal created
   if pc not in BY_ADDR:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   n={0x45a568:0,0x43de82:1,0x44104c:1,0x43dfa4:2,0x43f506:2}.get(pc,4 if pc==0x43f6b8 else 3)
   trace.append((BY_ADDR[pc],tuple(r[:n])))
   value=0
   if pc==0x45a568:value=role
   elif pc==0x43de82:created+=1;value=0x20080000+0x1000*created
   elif pc==0x44104c:value=r[0]^0x12345678
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_query_root_5e4f54'] if compiled else 0x5e4f54)|1,0x600000,count=400)
  return trace,u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((1,2,0xffffffff),(0,1,2,0x101,0xffffffff),(0,0x20070000)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:raise RuntimeError(f'case {i} {args}: {stock=} {source=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_ROOT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Device-role shift, mode narrowing, outer and inner LVGL call sequence and return','limits':['Lower LVGL and theme effects isolated; final object graph/layout remains open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
