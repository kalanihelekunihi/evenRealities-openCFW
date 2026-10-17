#!/usr/bin/env python3
"""Compare Terminal query overlapping-child counter with stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_hit_count_5eb576.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-hit-count-5eb576'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0
CALLS={'audio_terminal_query_height_5eb438':0x5eb438,'audio_uart_lv_obj_y_43fce0':0x43fce0,'audio_terminal_query_count_5eb30c':0x5eb30c,'audio_lv_child_44dce2':0x44dce2,'audio_uart_lv_obj_height_43fdda':0x43fdda}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,threshold,y,root,listptr,count,missing,height):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE+0x214,struct.pack('<I',root));u.mem_write(STATE+0x21c,struct.pack('<I',listptr))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,threshold);u.reg_write(A.UC_ARM_REG_R1,y&0xffffffff)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc not in CALLS.values():return
   a=cpu.reg_read(A.UC_ARM_REG_R0);b=cpu.reg_read(A.UC_ARM_REG_R1)
   if pc==0x5eb438:trace.append(('query_height',a));v=height
   elif pc==0x43fce0:trace.append(('obj_y',a));v=5 if a==listptr else ((a-0x20091000)//0x100)*8+2
   elif pc==0x5eb30c:trace.append(('count',));v=count
   elif pc==0x44dce2:trace.append(('child',a,b));v=0 if b==missing else 0x20091000+b*0x100
   else:trace.append(('obj_height',a));v=12
   cpu.reg_write(A.UC_ARM_REG_R0,v&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_query_hit_count_5eb576'] if compiled else 0x5eb576)|1,0x600000,count=600)
  return trace,u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,1,2,3,0x102),(-10,0,10),(0,0x20090000),(0,0x20091000),(0,1,2,3),(-1,0,1,2),(0,20)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:print('mismatch',i,args,stock,source);raise RuntimeError('query-hit-count mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_HIT_COUNT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Null gates, signed child geometry, count loop, threshold and return','limits':['Child getters are stubbed; LVGL tree mutation, final placement and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
