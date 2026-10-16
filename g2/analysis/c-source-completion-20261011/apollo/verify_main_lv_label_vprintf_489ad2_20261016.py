#!/usr/bin/env python3
"""Compare stock LVGL two-pass formatted-text allocator with C."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_label_vprintf_489ad2.c'
OUT=G2/'build/c-firmware/20261016/main-lv-label-vprintf-489ad2'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS=[('audio_uart_lv_vsnprintf_483fea',0x483fea),('audio_uart_lv_malloc',0x44f718),('audio_uart_lvgl_log',0x44d25c)]
FMT,VA,BUF=0x20001000,0x20002000,0x20005000
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
 def run(compiled,fmt,words,length,second_result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(FMT,fmt+b'\0'+bytes(30));u.mem_write(VA,struct.pack('<IIII',*words));u.mem_write(BUF,bytes([0xa5])*0x1000)
  trace=[];calls=0
  def hook(cpu,pc,size,_):
   nonlocal calls
   if pc not in cuts:return
   i=cuts[pc];r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if i==0:
    trace.append(('format',r[0],r[1],r[2],struct.unpack('<IIII',cpu.mem_read(r[3],16))))
    if calls==0:value=length
    else:
     data=bytes((0x40+j)%256 for j in range(min(length+1,0x1000)))
     cpu.mem_write(r[0],data);value=second_result
    calls+=1
   elif i==1:trace.append(('alloc',r[0]));value=BUF
   else:raise RuntimeError('unexpected log')
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,FMT);u.reg_write(A.UC_ARM_REG_R1,VA)
  entry=sym['audio_uart_lv_label_vprintf_489ad2'] if compiled else 0x489ad2;u.emu_start(entry|1,0x600000,count=300)
  return trace,bytes(u.mem_read(BUF,min(length+1,0x1000))),u.reg_read(A.UC_ARM_REG_R0)
 cases=0
 for fmt,words,length,second_result in itertools.product((b'%lus',b'%lum%02lus'),((0,1,2,3),(0xffffffff,0x12345678,0,42)),(0,1,8,127,255),(0,3,0xffffffff)):
  a,b=run(False,fmt,words,length,second_result),run(True,fmt,words,length,second_result)
  if a!=b:raise RuntimeError(f'mismatch {fmt=} {words=} {length=} {second_result=} {a[0]} {b[0]} {a[2]} {b[2]}')
  cases+=1
 result={'status':'PASS_EXPERIMENTAL_MAIN_LV_LABEL_VPRINTF_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':cases,'scope':'Two-pass formatter arguments, va-list forwarding, allocation size, output buffer and returned pointer','limits':['Allocation-failure fatal trap and real formatter effects outside bounded oracle; final placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],cases,sha(path))
if __name__=='__main__':main()
