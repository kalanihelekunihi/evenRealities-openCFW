#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate list layout refresh."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_main_list_layout_5b0d86.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-list-layout-5b0d86'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
PAIRS=[('audio_terminal_ui_object_valid_43e2ea',0x43e2ea,'valid',1),('audio_lv_delete_44d7b8',0x44d7b8,'delete',1),('audio_uart_page_43de82',0x43de82,'create',1),('audio_uart_buffer_zero',0x43c0e4,'zero',3),('audio_uart_page_44129e',0x44129e,'style1',3),('audio_uart_page_44131c',0x44131c,'style2',3),('audio_uart_page_44146a',0x44146a,'style3',3),('audio_conversate_ui_style_5b0ac4',0x5b0ac4,'style4',3),('audio_uart_page_43dfa4',0x43dfa4,'layout',2),('audio_uart_page_43f09a',0x43f09a,'position',3),('audio_uart_page_43f4c0',0x43f4c0,'size',3),('audio_uart_page_44104c',0x44104c,'color',1),('audio_uart_page_44127e',0x44127e,'bg',3),('audio_uart_page_43f6d6',0x43f6d6,'align',4),('audio_conversate_list_view_apply_5b0d24',0x5b0d24,'apply',2)]
LOWERS={name:(0x101010+i*0x10,native,kind,argc) for i,(name,native,kind,argc) in enumerate(PAIRS)}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_ui_main_list_layout_5b0d86','--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369','--defsym=audio_conversate_ui_app_id_200743a0=0x200743a0',*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in LOWERS.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,app,list_,old,valid,mode):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  base=0x20071368;cpu.mem_write(base,bytes([0x5a])*0xa0)
  for off,value in ((0x64,list_),(0x68,old)):
   cpu.mem_write(base+off,struct.pack('<I',value))
  cpu.mem_write(base+0x97,bytes([mode]));cpu.mem_write(0x200743a0,struct.pack('<I',app))
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
  events=[];done=[False];creates=[0];names={row[1 if native else 0]:(row[2],row[3]) for row in LOWERS.values()}
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   row=names.get(pc)
   if row is None:return
   kind,argc=row;r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   events.append((kind,*r[:argc]))
   ret=0
   if kind=='valid':ret=valid
   elif kind=='create':ret=0x20080000+creates[0]*0x100;creates[0]+=1
   elif kind=='color':ret=0x20005555
   elif kind=='zero':m.mem_write(r[0],bytes([r[2]&0xff])*r[1])
   m.reg_write(A.UC_ARM_REG_R0,ret);m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x5b0d86 if native else symbols['audio_conversate_ui_main_list_layout_5b0d86']
  cpu.emu_start(entry|1,0,count=1600)
  if not done[0]:raise RuntimeError('list layout did not return')
  return events,bytes(cpu.mem_read(base,0xa0))
 cases=[(app,list_,old,valid,mode) for app in (0,0x20001000) for list_ in (0,0x20002000) for old in (0,0x20003000) for valid in (0,1) for mode in (0,1,3)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'list layout mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_LIST_LAYOUT_5B0D86_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_body':'0x5b0d86..0x5b0edb','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['LVGL creation, validity, styling, alignment and mode apply remain controlled lower boundaries.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
