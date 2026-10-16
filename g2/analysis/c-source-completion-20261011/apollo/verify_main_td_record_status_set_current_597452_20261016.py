#!/usr/bin/env python3
"""Compare session status setter's entire TD-state mutation with stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/td_record_status_set_current_597452.c'
OUT=G2/'build/c-firmware/20261016/main-td-record-status-set-current-597452'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';TD=0x2010fd20;GETTER=0x5973dc;SIZE=0xa1dc
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',f'--defsym=audio_td_state=0x{TD:x}',f'--defsym=audio_terminal_counter_b_get_5973dc=0x{GETTER|1:x}',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,session,count,match_idx,status,active):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x200000);state=bytearray((i*5+17)&255 for i in range(SIZE));state[0xa1d9]=active;struct.pack_into('<I',state,0x9568,count)
  for i in range(10):
   struct.pack_into('<I',state,0x95fc+i*0x90,(session if i==match_idx else 100+i)&0xffffffff)
   state[0x9682+i*0x90]=0x66;state[0x9688+i*0x90]=0x77
  u.mem_write(TD,bytes(state));u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,status)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc!=GETTER:return
   trace.append('getter');cpu.reg_write(A.UC_ARM_REG_R0,session);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_td_record_status_set_current_597452'] if compiled else 0x597452)|1,0x600000,count=2000)
  return trace,bytes(u.mem_read(TD,SIZE))
 cases=list(itertools.product((0,42,0xffffffff),(0,1,10,11),(-1,0,3),(1,2,257),(0,1)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   diff=[j for j,(a,b) in enumerate(zip(stock[1],source[1])) if a!=b]
   print('mismatch',i,args,'trace',stock[0],source[0],'state offsets',diff[:16]);raise RuntimeError('status setter mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TD_RECORD_STATUS_SET_CURRENT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Session sentinel, active flag, ten-row cap, matching row and marked-byte clearing across entire TD state','limits':['Counter getter is isolated with controlled return; final TD RAM placement and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
