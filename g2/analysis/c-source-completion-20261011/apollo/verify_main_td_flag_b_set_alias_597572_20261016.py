#!/usr/bin/env python3
"""Compare flag-B setter alias and C provider against stock RAM effects."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/td_flag_b_set_alias_597572.c'
PROVIDER=G2/'components/audio/uart_thread_source_candidate/td_flag_set_with_reset.c'
OUT=G2/'build/c-firmware/20261016/main-td-flag-b-set-597572';PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2010fd20
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);objs=[];elf=OUT/'oracle.elf'
 for source in (SOURCE,PROVIDER):
  obj=OUT/(source.stem+'-oracle.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True);objs.append(obj)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',f'--defsym=audio_td_state=0x{STATE:x}',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,value,marker):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x120000);u.mem_write(STATE,bytes((i*13+marker)&255 for i in range(0xa1dc)))
  u.mem_write(STATE+0x9564,struct.pack('<I',0xffffffff if marker&1 else 0x12345678))
  u.reg_write(A.UC_ARM_REG_SP,0x2011f000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,value)
  def hook(cpu,pc,size,_):
   if pc!=0x43c0e4:return
   ptr=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1);byte=cpu.reg_read(A.UC_ARM_REG_R2)&255
   cpu.mem_write(ptr,bytes([byte])*n);cpu.reg_write(A.UC_ARM_REG_R0,ptr);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_td_flag_b_set_597572'] if compiled else 0x597572)|1,0x600000,count=3000)
  return bytes(u.mem_read(STATE,0xa1dc))
 cases=[(value,marker) for value in (0,1,2,0x100,0x101) for marker in (0,1,37,42)]
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   mismatch=next(j for j,(a,b) in enumerate(zip(stock,source)) if a!=b)
   print('mismatch',i,args,hex(mismatch),stock[mismatch],source[mismatch]);raise RuntimeError('TD flag-B mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TD_FLAG_B_SET_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'provider':str(PROVIDER.relative_to(ROOT)),'provider_sha256':sha(PROVIDER),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Flag-B setter and existing TD provider compare full 0xa1dc state bytes for reset/invalidate branches','limits':['Stock memset isolated; final RAM placement and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
