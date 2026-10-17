#!/usr/bin/env python3
"""Stock/C lower-call replay for complete Conversate display-main-page route."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_display_main_page_5b2d64.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261016/main-conversate-display-main-page-5b2d64'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
DATA={'audio_conversate_display_tick_5b22ee':0x5b22ef,'audio_conversate_machine_context_200e3aec':0x200e3aec,'audio_conversate_prep_icon_76a47c':0x76a47c,'audio_conversate_title_label_5b3334':0x5b3334,'audio_conversate_ui_app_id_200743a0':0x200743a0,'audio_conversate_ui_settings_extension_20071369':0x20071369,'audio_uart_ring_primary_head_cell':0x200746dc}
SPECIAL={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
ARGC={0x5b4766:0,0x43d0ce:0,0x5b0d86:0,0x44d7b8:1,0x43de82:1,0x499416:1,0x5b12ba:1,0x460084:1,0x44104c:1,0x43dfa4:2,0x58c7a0:2,0x5b22fa:2,0x43ded4:2,0x44e368:2,0x49942e:2,0x499678:2,0x43f6ac:2,0x45fffe:2,0x5b1150:3,0x43f6b8:4,0x43f6d6:4}
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj,elf_path=OUT/'oracle.o',OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines() if line.strip()]
 funcs=[name for name in imports if name not in DATA]
 lower={name:(0x101000+i*0x10,SPECIAL.get(name,int(name[-6:],16) if name not in SPECIAL else 0)) for i,name in enumerate(funcs)}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_conversate_ui_route_5b2d64',*[f'--defsym={name}=0x{addr:x}' for name,addr in DATA.items()],*[f'--defsym={name}=0x{row[0]|1:x}' for name,row in lower.items()],str(obj),'-o',str(elf_path)],check=True,capture_output=True)
 with elf_path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,running,old_root,old_overlay,notes_present,flags,elapsed):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  cpu.mem_map(0x438000,(len(payload)+4095)&~4095);cpu.mem_write(0x438000,payload)
  cpu.mem_map(0x100000,0x20000);cpu.mem_map(0x20000000,0x100000)
  if not native:
   for start,data in segments:
    if data:cpu.mem_write(start,data)
  base=0x20071368;cpu.mem_write(base,bytes([0x5a])*0xb0)
  for off,value in ((4,old_root),(12,old_overlay),(0x64,0x2000aa00),(0x7c,0x2000bb00),(0x80,0x2000cc00),(0x84,3)):
   cpu.mem_write(base+off,struct.pack('<I',value))
  cpu.mem_write(base+0x8c,bytes([0 if notes_present else 1]));cpu.mem_write(base+0x8d,b'\x00')
  cpu.mem_write(0x200e3aec,bytes([running]))
  cpu.mem_write(0x200743a0,struct.pack('<I',0x20001000))
  cpu.mem_write(0x200746dc,struct.pack('<I',0x2000d000))
  cpu.mem_write(0x2000d00c,struct.pack('<I',11))
  cpu.mem_write(0x20007000,bytes(0x100))
  if notes_present:
   cpu.mem_write(0x20007000,struct.pack('<H',1))
   cpu.mem_write(0x20007084,struct.pack('<I',1))
  cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000);cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
  for reg,val in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),(0x20001234,elapsed,0x20005678,0x20009abc)):
   cpu.reg_write(reg,val)
  events=[];done=[False];creates=[0];labels=[0]
  names={row[1 if native else 0]:name for name,row in lower.items()}
  def cstr(m,a):return bytes(m.mem_read(a,200)).split(b'\0',1)[0].decode(errors='replace')
  def hook(m,pc,_size,_user):
   if pc==0x101f00:done[0]=True;m.emu_stop();return
   name=names.get(pc)
   if name is None:return
   addr=lower[name][1];r=[m.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if addr==0x43d574:
    sp=m.reg_read(A.UC_ARM_REG_SP);line,msg=struct.unpack('<II',m.mem_read(sp,8))
    arg=struct.unpack('<I',m.mem_read(sp+8,4))[0]
    events.append((addr,r[0],cstr(m,r[1]),cstr(m,r[2]),cstr(m,r[3]),line,cstr(m,msg),arg))
   elif addr==0x43ce9e:events.append((addr,r[0],cstr(m,r[1]),cstr(m,r[2])))
   elif addr==0x460084:events.append((addr,cstr(m,r[0])))
   elif addr==0x45fffe:events.append((addr,cstr(m,r[0]),r[1]))
   else:events.append((addr,*r[:ARGC.get(addr,3)]))
   ret=0
   if addr==0x5b4766:ret=0x20007000
   elif addr==0x43d0ce:ret=flags
   elif addr==0x43de82:ret=0x20010000+creates[0]*0x100;creates[0]+=1
   elif addr==0x499416:ret=0x20011000+labels[0]*0x100;labels[0]+=1
   elif addr==0x58c7a0:ret=0x20012000
   elif addr==0x5b12ba:ret=0x20013000
   elif addr==0x460084:ret=0x1234
   elif addr==0x45fffe:ret=0x20014000
   elif addr==0x5b1150:ret=0x20015000
   elif addr==0x44104c:ret=r[0]^0xa5a5a5
   m.reg_write(A.UC_ARM_REG_R0,ret);m.reg_write(A.UC_ARM_REG_PC,m.reg_read(A.UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  entry=0x5b2d64 if native else symbols['audio_conversate_ui_route_5b2d64']
  cpu.emu_start(entry|1,0,count=2600)
  if not done[0]:raise RuntimeError('display main page did not return')
  return events,cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(base,0xa0))
 cases=[(running,old_root,old_overlay,notes_present,flags,elapsed) for running in (0,1) for old_root in (0,0x20002000) for old_overlay in (0,0x20003000) for notes_present in (0,1) for flags in (0,1,2,4,7) for elapsed in (0,125)]
 for case in cases:
  native,compiled=run(True,*case),run(False,*case)
  if native!=compiled:raise RuntimeError(f'display-main-page mismatch {case}: {native} != {compiled}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_MAIN_PAGE_5B2D64_C','stock_payload_sha256':PAYLOAD_SHA,'cases':len(cases),'native_body':'0x5b2d64..0x5b30c7','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['UI child routines, LVGL and logs remain controlled lower boundaries.','Three ROM/configuration objects and scroll helper remain source gates.']}
 receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(cases),hashlib.sha256(receipt.read_bytes()).hexdigest())
if __name__=='__main__':main()
