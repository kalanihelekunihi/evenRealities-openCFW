#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate prep-notes button factory."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_prep_button_5b1150.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-prep-button-5b1150'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ADDRS=[0x43de82,0x43f4c0,0x48ba78,0x48ba92,0x44146a,0x441254,0x44122a,0x441238,0x44131c,0x44130c,0x44129e,0x44132a,0x44104c,0x4412ec,0x43dfa4,0x498668,0x498680,0x44127e,0x4413ce,0x499416,0x49942e,0x44143e,0x441180,0x4411aa,0x499678,0x44145a,0x44140e,0x43d0ce,0x43d574,0x43ce9e]
NAMES={0x43de82:'audio_uart_page_43de82',0x498668:'audio_lv_image_create_498668',0x498680:'audio_lv_image_source_498680',0x499416:'audio_lv_label_create_499416',0x49942e:'audio_lv_label_text_49942e',0x499678:'audio_lv_label_mode_499678',0x43d0ce:'audio_log_flags',0x43d574:'audio_log_extended',0x43ce9e:'compressed_log_output'}
LOWERS={NAMES.get(a,f'audio_uart_page_{a:x}'):(0x101010+i*0x10,a) for i,a in enumerate(ADDRS)}
ARGC={0x43de82:1,0x48ba78:2,0x48ba92:4,0x44104c:1,0x43dfa4:2,0x498668:1,0x498680:2,0x499416:1,0x49942e:2,0x499678:2,0x43d0ce:0}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_prep_button_create_5b1150','--defsym=audio_uart_ring_primary_head_cell=0x200746dc',*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in LOWERS.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,parent,image,label,flags):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  cpu.mem_write(0x200746dc,struct.pack('<I',0x2000d000))
  cpu.mem_write(0x20005000,b'prep notes\0')
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
  for reg,val in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),(parent,image,label,0x1234)):cpu.reg_write(reg,val)
  events=[];done=[False];names={row[1 if native else 0]:name for name,row in LOWERS.items()}
  def cstr(m,a):return bytes(m.mem_read(a,200)).split(b'\0',1)[0].decode()
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   name=names.get(pc)
   if name is None:return
   a=LOWERS[name][1]
   r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if a==0x43d574:
    line,msg,arg=struct.unpack('<III',m.mem_read(m.reg_read(A.UC_ARM_REG_SP),12))
    events.append((a,r[0],cstr(m,r[1]),cstr(m,r[2]),cstr(m,r[3]),line,cstr(m,msg),arg))
   elif a==0x43ce9e:events.append((a,r[0],cstr(m,r[1]),cstr(m,r[2]),r[3]))
   else:events.append((a,*r[:ARGC.get(a,3)]))
   ret=0x20003000 if a==0x43de82 else 0x20004000 if a==0x498668 else 0x20007000 if a==0x499416 else (r[0]^0xa5a5a5) if a==0x44104c else flags if a==0x43d0ce else 0
   m.reg_write(A.UC_ARM_REG_R0,ret);m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x5b1150 if native else symbols['audio_conversate_prep_button_create_5b1150']
  cpu.emu_start(entry|1,0,count=800)
  if not done[0]:raise RuntimeError('prep button did not return')
  return events,cpu.reg_read(A.UC_ARM_REG_R0)
 cases=[(parent,image,label,flags) for parent in (0,0x20001000) for image in (0,0x20006000) for label in (0,0x20005000) for flags in (0,1,2,4,7)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'prep button mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_PREP_BUTTON_5B1150_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_body':'0x5b1150..0x5b12b9','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['LVGL object, image, label and log functions remain controlled lower boundaries.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
