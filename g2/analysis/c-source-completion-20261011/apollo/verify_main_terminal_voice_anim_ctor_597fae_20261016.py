#!/usr/bin/env python3
"""Compare animimage constructor state and lower animation calls with stock."""
import hashlib,itertools,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_ctor_597fae.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-ctor-597fae'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';OBJECT=0x20080000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_uart_lv_anim_init_4503d6':0x4503d7,'audio_uart_lv_anim_values_4506ce':0x4506cf,'audio_terminal_voice_anim_exec_598008':0x598009}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,seed,cls):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(OBJECT,bytes((seed+i*17)&255 for i in range(0xc40)))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,cls);u.reg_write(A.UC_ARM_REG_R1,OBJECT)
  trace=[]
  def hook(cpu,pc,size,_):
   if pc==0x4503d6:trace.append(('init',cpu.reg_read(A.UC_ARM_REG_R0)))
   elif pc==0x4506ce:trace.append(('values',tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))))
   else:return
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_voice_anim_ctor_597fae'] if compiled else 0x597fae)|1,0x600000,count=180)
  return trace,bytes(u.mem_read(OBJECT,0xc40))
 cases=list(itertools.product((0,1,17,255),(0,0x7550dc,0xffffffff)))
 for i,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:
   print('mismatch',i,args,'trace',a[0],b[0],'bytes',[(j,x,y) for j,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:20]);raise RuntimeError('anim ctor mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_CTOR_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Animimage object fields, animation descriptor setup and callback pointer','limits':['Animation init/values effects isolated; callback 0x598008 and final LVGL object behavior open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
