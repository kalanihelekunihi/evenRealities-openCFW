#!/usr/bin/env python3
"""Compare stock animimage factory calls and class record with C source."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_factory_597e90.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-factory-597e90'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_uart_image_class_756108':0x756108,'audio_terminal_voice_anim_ctor_597fae':0x597faf,'audio_uart_page_create_44cf98':0x44cf99,'audio_uart_page_initialize_44d0f0':0x44d0f1}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,parent):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,parent)
  trace=[]
  def cstr(cpu,p):return bytes(cpu.mem_read(p,40)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   if pc==0x44cf98:
    ptr=cpu.reg_read(A.UC_ARM_REG_R0);arg=cpu.reg_read(A.UC_ARM_REG_R1)
    words=struct.unpack('<9I',cpu.mem_read(ptr,36))
    trace.append(('create',words[:5],cstr(cpu,words[5]),words[6:],arg))
    cpu.reg_write(A.UC_ARM_REG_R0,0x20080000)
   elif pc==0x44d0f0:trace.append(('init',cpu.reg_read(A.UC_ARM_REG_R0)))
   else:return
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_voice_anim_create_597e90'] if compiled else 0x597e90)|1,0x600000,count=80)
  return trace,u.reg_read(A.UC_ARM_REG_R0)
 cases=(0,0x20081000,0xffffffff)
 for i,parent in enumerate(cases):
  stock=run(False,parent);source=run(True,parent)
  if stock!=source:raise RuntimeError(f'case {i}: {stock=} {source=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_FACTORY_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Source-owned 36-byte lv_animimg class fields and name, factory call order and return','limits':['Class constructor 0x597fae and lower LVGL creation/init effects isolated; whole object behavior remains open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
