#!/usr/bin/env python3
"""Stock/C lower-call replay for Apollo LVGL label rule wrapper."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_label_rule_43f6ac.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-lv-label-rule-43f6ac'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_uart_page_43f6ac','--defsym=audio_uart_page_4411d4=0x101011',str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,obj_,value):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
  cpu.reg_write(A.UC_ARM_REG_R0,obj_);cpu.reg_write(A.UC_ARM_REG_R1,value)
  events=[];done=[False]
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   if pc!=(0x4411d4 if native else 0x101010):return
   events.append(tuple(m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)))
   m.reg_write(A.UC_ARM_REG_R0,0);m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  cpu.emu_start((0x43f6ac if native else symbols['audio_uart_page_43f6ac'])|1,0,count=70)
  if not done[0]:raise RuntimeError('label rule did not return')
  return events
 cases=[(obj_,value) for obj_ in (0,0x20001000) for value in (0,4,0xff,0x100,0x1234)]
 for case in cases:
  if run(True,*case)!=run(False,*case):raise RuntimeError(f'label rule mismatch {case}')
 record={'status':'PASS_DIRECT_MAIN_LV_LABEL_RULE_43F6AC_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_body':'0x43f6ac..0x43f6b7','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Underlying LVGL setter remains a controlled lower boundary.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
