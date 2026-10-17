#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate animated prep-notes indicator."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_pre_notes_anim_58c7a0.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-pre-notes-anim-58c7a0'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
PAIRS=[('audio_terminal_voice_anim_create_597e90',0x597e90,'create',1),('audio_lv_label_style_call_597ea6',0x597ea6,'sources',3),('audio_lv_label_style_call_597f10',0x597f10,'duration',2),('audio_lv_label_style_call_597f52',0x597f52,'repeat',2),('audio_conversate_route_get_release_pair_597f82',0x597f82,'pair',1),('audio_uart_page_44104c',0x44104c,'color',1),('audio_uart_page_44127e',0x44127e,'bg',3),('audio_uart_page_44129e',0x44129e,'opacity',3),('audio_lv_label_style_call_597ee0',0x597ee0,'start',1)]
LOWERS={name:(0x101010+i*0x10,native,kind,argc) for i,(name,native,kind,argc) in enumerate(PAIRS)}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_pre_notes_anim_create_58c7a0','--defsym=audio_conversate_anim_frames_20000bf4=0x20000bf4',*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in LOWERS.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,parent,complete,created,pair):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  cpu.mem_write(0x20006000,bytes([0x5a])*0x60)
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
  cpu.reg_write(A.UC_ARM_REG_R0,parent);cpu.reg_write(A.UC_ARM_REG_R1,complete)
  events=[];done=[False];names={row[1 if native else 0]:(row[2],row[3]) for row in LOWERS.values()}
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   row=names.get(pc)
   if row is None:return
   kind,argc=row;r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   events.append((kind,*r[:argc]))
   ret=created if kind=='create' else pair if kind=='pair' else 0x123456 if kind=='color' else 0
   m.reg_write(A.UC_ARM_REG_R0,ret);m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x58c7a0 if native else symbols['audio_conversate_pre_notes_anim_create_58c7a0']
  cpu.emu_start(entry|1,0,count=500)
  if not done[0]:raise RuntimeError('pre-notes anim did not return')
  return events,cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(0x20006000,0x60))
 cases=[(parent,complete,created,pair) for parent in (0,0x20001000) for complete in (0,0x58c825) for created in (0,0x20003000) for pair in (0,0x20006000)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'pre-notes anim mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_PRE_NOTES_ANIM_58C7A0_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_bodies':['0x58c7a0..0x58c823','0x58c824..0x58c835'],'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Six-frame RAM pointer array at 0x20000bf4 has no source owner yet.','LVGL animation calls remain controlled lower boundaries.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
