#!/usr/bin/env python3
"""Stock/C lower-call replay for bounce phase-2 callback and Y setter."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_bounce_phase2_58a5a4.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-bounce-phase2-58a5a4'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
LOWERS={'audio_uart_page_43f142':(0x101010,0x43f142,'set_y'),'audio_log_flags':(0x101020,0x43d0ce,'flags'),'audio_log_extended':(0x101030,0x43d574,'extended'),'compressed_log_output':(0x101040,0x43ce9e,'compact')}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_bounce_phase2_done_58a5a4','--defsym=audio_conversate_bounce_state_20073e14=0x20073e14',*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in LOWERS.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,kind,active,other,callback,flags):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  state=0x20073e14;alt=0x20050000;descriptor=0x20060000
  cpu.mem_write(state,struct.pack('<IIII',active,40,1,0x101091 if callback else 0))
  cpu.mem_write(alt,struct.pack('<IIII',other,55,0,0))
  context=0 if kind==0 else state if kind==1 else alt
  cpu.mem_write(descriptor+28,struct.pack('<I',context))
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01);cpu.reg_write(A.UC_ARM_REG_R0,descriptor)
  events=[];done=[False];names={row[1 if native else 0]:row[2] for row in LOWERS.values()};names[0x101090]='callback'
  def cstr(m,a):return bytes(m.mem_read(a,200)).split(b'\0',1)[0].decode()
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   action=names.get(pc)
   if action is None:return
   r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if action=='flags':events.append((action,))
   elif action=='callback':events.append((action,r[0]))
   elif action=='set_y':events.append((action,*r[:2]))
   elif action=='extended':
    line,msg=struct.unpack('<II',m.mem_read(m.reg_read(A.UC_ARM_REG_SP),8))
    events.append((action,r[0],cstr(m,r[1]),cstr(m,r[2]),cstr(m,r[3]),line,cstr(m,msg)))
   else:events.append((action,r[0],cstr(m,r[1]),cstr(m,r[2])))
   m.reg_write(A.UC_ARM_REG_R0,flags if action=='flags' else 0)
   m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x58a5a4 if native else symbols['audio_conversate_bounce_phase2_done_58a5a4']
  cpu.emu_start(entry|1,0,count=500)
  if not done[0]:raise RuntimeError('phase2 did not return')
  return events,bytes(cpu.mem_read(state,16))
 cases=[(kind,active,other,callback,flags) for kind in (0,1,2) for active in (0,0x20001000) for other in (0,0x20002000) for callback in (0,1) for flags in (0,1,2,4,7)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'phase2 mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PHASE2_58A5A4_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_bodies':['0x58a598..0x58a5a3','0x58a5a4..0x58a67f'],'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['LVGL and log functions remain lower boundaries.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
