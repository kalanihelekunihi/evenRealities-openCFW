#!/usr/bin/env python3
"""Controlled stock/C comparison for text-stream completion and timer scheduling."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_schedule_552f6a.c'
OUT=G2/'build/c-firmware/20261016/main-text-stream-schedule'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nchar*strcpy(char*a,const char*b){(void)b;return a;}\nuint32_t audio_text_stream_buffer_create_553338(void*a,void**b,uint32_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}\nint32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}\nint32_t audio_file_mutex_release(void*a){(void)a;return 0;}\nvoid*audio_uart_timer_new(void(*a)(void*),uint32_t b,void*c,const void*d){(void)a;(void)b;(void)c;(void)d;return 0;}\nint32_t audio_timer_stop(void*a){(void)a;return 0;}\nint32_t audio_timer_start(void*a,uint32_t b){(void)a;(void)b;return 0;}\nint32_t audio_timer_delete(void*a){(void)a;return 0;}\nuint32_t audio_log_flags(void){return 0;}\nvoid audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\nuint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\nvoid audio_text_stream_tick_553054(void*a){(void)a;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,copied,total,notify,mutex,timer,lock_result,created,start_result,capacity_ok,callback,log_flags):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 obj=0x20003000;dst=0x20004000;src=0x20005000;cb=0x100800
 seed=bytearray([0xa5]*0x30)
 for off,value in ((0,dst),(4,src),(8,25),(0x0c,copied),(0x10,total),(0x18,cb|1 if callback else 0),(0x1c,0x20007000 if timer else 0),(0x20,0x20006000 if mutex else 0),(0x24,64)):
  seed[off:off+4]=value.to_bytes(4,'little')
 cpu.mem_write(obj,bytes(seed));cpu.mem_write(dst,b'AB\0');cpu.mem_write(src,b'ABCDE\0')
 cpu.reg_write(UC_ARM_REG_R0,obj);cpu.reg_write(UC_ARM_REG_R1,notify);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x553338:'capacity',0x48d540:'strcpy',0x4497b6:'lock',0x44981c:'unlock',0x4493b0:'new',0x4494d8:'stop',0x449498:'start',0x44953e:'delete',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed',cb:'callback'}
 names={'audio_text_stream_buffer_create_553338':'capacity','strcpy':'strcpy','audio_file_mutex_acquire':'lock','audio_file_mutex_release':'unlock','audio_uart_timer_new':'new','audio_timer_stop':'stop','audio_timer_start':'start','audio_timer_delete':'delete','audio_log_flags':'flags','audio_log_extended':'extended','compressed_log_output':'compressed'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock;hooks[cb]='callback';calls=[]
 def readstr(machine,p):
  out=bytearray();i=0
  while (c:=machine.mem_read(p+i,1)[0])!=0:out.append(c);i+=1
  return bytes(out)
 def hook(machine,pc,width,unused):
  kind=hooks.get(pc)
  if kind is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if kind=='capacity':calls.append((kind,a,b,c,d));result=int(capacity_ok)
  elif kind=='strcpy':cpu.mem_write(a,readstr(machine,b)+b'\0');calls.append((kind,a,b));result=a
  elif kind=='lock':calls.append((kind,a,b));result=lock_result
  elif kind=='new':calls.append((kind,'callback',b,c,d));result=0x20008000 if created else 0
  elif kind=='start':calls.append((kind,a,b));result=start_result
  elif kind=='flags':calls.append((kind,));result=log_flags
  elif kind=='callback':calls.append((kind,a));result=0
  elif kind in ('extended','compressed'):calls.append((kind,a));result=0
  else:calls.append((kind,a));result=0
  machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_text_stream_schedule_552f6a'] if compiled else 0x552f6a
 cpu.emu_start(entry|1,0x600000,count=2000)
 return bytes(cpu.mem_read(obj,0x30)),bytes(cpu.mem_read(dst,32)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'schedule-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'schedule-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_text_stream_schedule_552f6a',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 caseset=itertools.product(((0,5),(4,5),(5,5),(6,5),(0x80000000,1)),(0,1,257),(False,True),(False,True),(0,1),(False,True),(0,1),(False,True),(False,True),(0,1,2,4,7))
 for pair,notify,mutex,timer,lock_result,created,start_result,capacity_ok,callback,log_flags in caseset:
  args=(*pair,notify,mutex,timer,lock_result,created,start_result,capacity_ok,callback,log_flags)
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'schedule mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_TEXT_STREAM_SCHEDULE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Signed copied/total, copy, callback, mutex, timer create/stop/start/delete, zero log flags','limits':['Child side effects and full timer callback remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
