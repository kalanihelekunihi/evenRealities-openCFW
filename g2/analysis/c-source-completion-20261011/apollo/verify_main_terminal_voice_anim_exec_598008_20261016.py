#!/usr/bin/env python3
"""Compare animimage frame selection and null-descriptor log with stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_exec_598008.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-exec-598008'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OBJECT=0x20080000;FRAMES=0x20081010
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_uart_lvgl_log=0x44d25d','--defsym=audio_uart_page_498680=0x498681',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,available,count,index):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(OBJECT,bytes(0x1000))
  u.mem_write(OBJECT+0xbc,struct.pack('<I',FRAMES if available else 0));u.mem_write(OBJECT+0xc0,bytes([count&255]))
  for j in range(-2,8):u.mem_write(FRAMES+j*4,struct.pack('<I',0x600000+j*0x100))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,OBJECT);u.reg_write(A.UC_ARM_REG_R1,index&0xffffffff)
  trace=[]
  def cstr(cpu,p):return bytes(cpu.mem_read(p,150)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   if pc==0x44d25c:
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    msg=struct.unpack('<I',cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4))[0]
    trace.append(('log',r[0],cstr(cpu,r[1]),r[2],cstr(cpu,r[3]),cstr(cpu,msg)))
   elif pc==0x498680:trace.append(('source',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
   else:return
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_voice_anim_exec_598008'] if compiled else 0x598008)|1,0x600000,count=120)
  return trace
 cases=list(itertools.product((0,1),(1,3,5),(0,1,2,3,4,5)))
 for i,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:raise RuntimeError(f'case {i} {args}: {a=} {b=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_EXEC_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Null descriptor log and bounded frame-index clamp/source selection','limits':['Lower LVGL log/image-source effects isolated; malformed frame count and concurrent descriptor mutation remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
