#!/usr/bin/env python3
"""Controlled stock comparison for lv_label_set_text_fmt at 0x49954c."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_label_text_fmt_49954c.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-label-text-fmt-49954c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS=[('audio_uart_lvgl_log',0x44d25c),('audio_uart_page_invalidate_440656',0x440656),('audio_uart_lv_heap_free',0x44f758),('audio_uart_lv_label_vprintf_489ad2',0x489ad2),('audio_uart_page_layout_update_49a602',0x49a602)]
LABEL,FMT,OLD,NEW=0x20001000,0x20002000,0x20003000,0x20004000
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
 elf,seg,sym=build();cuts={a:i for i,(_,a) in enumerate(CALLS)}
 def run(compiled,old,static,fmt,args):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,data in seg:u.mem_write(a,data)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(LABEL,bytes((i*7+19)&255 for i in range(0x80)));u.mem_write(FMT,fmt+b'\0'+bytes(50));u.mem_write(OLD,b'old\0');u.mem_write(NEW,b'new\0')
  u.mem_write(LABEL+0x2c,struct.pack('<I',OLD if old else 0));u.mem_write(LABEL+0x5c,bytes([0x10 if static else 0]))
  trace=[]
  def hook(cpu,pc,size,_):
   if pc not in cuts:return
   i=cuts[pc];r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   if i==1:trace.append(('invalidate',r0))
   elif i==2:trace.append(('free',r0))
   elif i==3:
    trace.append(('format',r0,struct.unpack('<IIII',cpu.mem_read(r1,16))))
    cpu.reg_write(A.UC_ARM_REG_R0,NEW)
   elif i==4:trace.append(('layout',r0))
   else:raise RuntimeError('unexpected log')
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);sp=0x200ff000;u.reg_write(A.UC_ARM_REG_SP,sp);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,value in ((A.UC_ARM_REG_R0,LABEL),(A.UC_ARM_REG_R1,FMT),(A.UC_ARM_REG_R2,args[0]),(A.UC_ARM_REG_R3,args[1])):u.reg_write(reg,value)
  u.mem_write(sp,struct.pack('<II',args[2],args[3]))
  entry=sym['audio_lv_label_set_text_fmt_49954c'] if compiled else 0x49954c
  u.emu_start(entry|1,0x600000,count=500)
  return trace,bytes(u.mem_read(LABEL,0x70)),u.reg_read(A.UC_ARM_REG_R0)
 cases=0
 for old,static,fmt,args in itertools.product((0,1),(0,1),(b'%lus',b'%lum%02lus',b'%08x:%d:%d:%d'),((0,1,2,3),(1,0x12345678,0xffffffff,0xabcdefff),(0xffffffff,0,0,0))):
  a,b=run(False,old,static,fmt,args),run(True,old,static,fmt,args)
  if a!=b:
   print('mismatch',old,static,fmt,args,'traces',a[0],b[0],'ret',a[2],b[2]);print('bytes',[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:20]);raise RuntimeError('formatted label mismatch')
  cases+=1
 result={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_FMT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':cases,'scope':'Variadic register/stack forwarding, old text ownership, static bit, returned label and layout call','limits':['Null pointer fatal branches and real formatter side effects outside this bounded oracle; final placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],cases,sha(path))
if __name__=='__main__':main()
