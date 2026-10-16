#!/usr/bin/env python3
"""Compare four LVGL animimage setters/start with authenticated Apollo stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_animimage_597ea6.c'
OUT=G2/'build/c-firmware/20261016/main-lv-animimage-597ea6'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FUNCS=[('audio_lv_label_style_call_597ea6',0x597ea6),('audio_lv_label_style_call_597ee0',0x597ee0),('audio_lv_label_style_call_597f10',0x597f10),('audio_lv_label_style_call_597f52',0x597f52)]
CALLS=[('audio_uart_lvgl_log',0x44d25c),('audio_uart_lv_anim_values_4506ce',0x4506ce),('audio_uart_lv_anim_start_450408',0x450408)]
OBJ,SRC=0x20001000,0x20003000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}=0x{a|1:x}' for n,a in CALLS],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 return elf,seg,sym

def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 elf,seg,sym=build()
 def run(compiled,kind,object,value1,value2):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(OBJ,bytes((i*11+27)&255 for i in range(0xd0)));u.mem_write(SRC,bytes(range(64)))
  trace=[]
  def cstr(cpu,p):return bytes(cpu.mem_read(p,180)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   if pc not in (0x44d25c,0x4506ce,0x450408):return
   r=[cpu.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if pc==0x44d25c:
    sp=cpu.reg_read(A.UC_ARM_REG_SP);words=struct.unpack('<III',cpu.mem_read(sp,12));trace.append(('log',r[0],cstr(cpu,r[1]),r[2],cstr(cpu,r[3]),*(cstr(cpu,x) for x in words)))
   elif pc==0x4506ce:trace.append(('values',r[0],r[1]))
   else:trace.append(('start',r[0]))
   cpu.reg_write(A.UC_ARM_REG_R0,0x12345678);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  def fault(cpu,access,address,size,value,_):trace.append(('fault_write',address,size,value));return False
  u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,object);u.reg_write(A.UC_ARM_REG_R1,value1);u.reg_write(A.UC_ARM_REG_R2,value2)
  name,address=FUNCS[kind];entry=sym[name] if compiled else address
  try:u.emu_start(entry|1,0x600000,count=250)
  except UcError:
   if not trace or trace[-1][0]!='fault_write':raise
  return trace,bytes(u.mem_read(OBJ,0xd0))
 cases=[]
 for kind in range(4):
  for value1,value2 in itertools.product((0,1,0x20003000,0xffffffff),(0,1,0x12345678,0xffffffff)):
   cases.append((kind,OBJ,value1,value2))
  cases.append((kind,0,0x20003000,0x12345678))
 for idx,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:
   print('case',idx,args,'stock',a[0],'compiled',b[0]);print('bytes',[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:20]);raise RuntimeError('animimage mismatch')
 result={'status':'PASS_EXPERIMENTAL_MAIN_LV_ANIMIMAGE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Four animimage setter/start routines, object writes, lower call arguments, null assertion log and fault write','limits':['Real animation side effects and final placement remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],len(cases),sha(path))
if __name__=='__main__':main()
