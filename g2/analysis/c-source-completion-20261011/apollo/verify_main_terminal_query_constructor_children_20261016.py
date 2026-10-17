#!/usr/bin/env python3
"""Compare query four-margin and gap-style forwarding helpers with stock."""
import hashlib,itertools,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';OUT=G2/'build/c-firmware/20261016/main-terminal-query-construct-5eb8da'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_query_four_margins_5eb2bc.c',G2/'components/audio/uart_thread_source_candidate/terminal_query_gap_style_441262.c']
TARGETS=[('audio_terminal_query_four_margins_5eb2bc',0x5eb2bc,[0x44122a,0x441238,0x44120e,0x44121c]),('audio_uart_page_441262',0x441262,[0x44be4c])]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);total=0;elf_hashes=[]
 for source,(symbol,native,calls) in zip(SOURCES,TARGETS):
  obj=OUT/(source.stem+'-oracle.o');elf=OUT/(source.stem+'-oracle.elf')
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
  defs={'audio_uart_page_44122a':0x44122b,'audio_uart_page_441238':0x441239,'audio_uart_page_44120e':0x44120f,'audio_uart_page_44121c':0x44121d,'audio_uart_page_style_apply_44be4c':0x44be4d}
  subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
  elf_hashes.append(sha(elf))
  with elf.open('rb') as f:
   e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];compiled_addr=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name==symbol)
  def run(compiled,object_,value,selector):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
   u.reg_write(A.UC_ARM_REG_R0,object_);u.reg_write(A.UC_ARM_REG_R1,value);u.reg_write(A.UC_ARM_REG_R2,selector)
   trace=[]
   def hook(cpu,pc,size,_):
    if pc not in calls:return
    r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    trace.append((pc,r[:4 if pc==0x44be4c else 3]));cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((compiled_addr if compiled else native)|1,0x600000,count=80)
   return trace
  for i,args in enumerate(itertools.product((0,0x20090000),(0,1,6,0x102),(0,3))):
   stock=run(False,*args);source_trace=run(True,*args)
   if stock!=source_trace:print('mismatch',symbol,i,args,stock,source_trace);raise RuntimeError('query-constructor helper mismatch')
   total+=1
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_CONSTRUCTOR_CHILDREN_C_ORACLE','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'payload_sha256':PIN,'oracle_elf_sha256':elf_hashes,'cases':total,'scope':'Four-margin call order and style property 0x19 forwarding','limits':['Lower LVGL style mutation and hardware remain open.']}
 p=OUT/'children-oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],total,sha(p))
if __name__=='__main__':main()
