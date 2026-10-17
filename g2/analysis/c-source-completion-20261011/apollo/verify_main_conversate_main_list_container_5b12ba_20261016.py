#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate main-list container."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_main_list_container_5b12ba.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-list-container-5b12ba'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
PAIRS=[('audio_uart_page_43de82',0x43de82,'create'),('audio_uart_page_43f4c0',0x43f4c0,'size'),('audio_uart_page_48ba78',0x48ba78,'list'),('audio_uart_page_48ba92',0x48ba92,'config'),('audio_uart_page_441246',0x441246,'style0'),('audio_conversate_ui_style_5b0ac4',0x5b0ac4,'style1'),('audio_uart_page_44129e',0x44129e,'style2'),('audio_uart_page_44131c',0x44131c,'style3'),('audio_uart_page_44146a',0x44146a,'style4'),('audio_uart_page_441386',0x441386,'style5'),('audio_uart_page_44e368',0x44e368,'scroll'),('audio_uart_page_43ded4',0x43ded4,'flag'),('audio_uart_page_43dfa4',0x43dfa4,'layout')]
LOWERS={name:(0x101010+i*0x10,native,kind) for i,(name,native,kind) in enumerate(PAIRS)}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_ui_main_list_container_5b12ba',*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in LOWERS.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,parent,list_):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01);cpu.reg_write(A.UC_ARM_REG_R0,parent)
  events=[];done=[False];names={row[1 if native else 0]:row[2] for row in LOWERS.values()}
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   action=names.get(pc)
   if action is None:return
   r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   events.append((action,*r[:1 if action=='create' else 2 if action in ('list','scroll','flag','layout') else 4 if action=='config' else 3]))
   m.reg_write(A.UC_ARM_REG_R0,list_ if action=='create' else 0)
   m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x5b12ba if native else symbols['audio_conversate_ui_main_list_container_5b12ba']
  cpu.emu_start(entry|1,0,count=350)
  if not done[0]:raise RuntimeError('list container did not return')
  return events,cpu.reg_read(A.UC_ARM_REG_R0)
 cases=[(parent,list_) for parent in (0,0x20001000,0x20002000) for list_ in (0,0x20003000,0x20004000)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'list container mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_LIST_CONTAINER_5B12BA_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_body':'0x5b12ba..0x5b133b','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['LVGL creation and styling are controlled lower boundaries.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
