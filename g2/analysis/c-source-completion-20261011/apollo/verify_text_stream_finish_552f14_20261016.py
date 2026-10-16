#!/usr/bin/env python3
"""Controlled stock/C comparison for text-stream finish and copy."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_finish_552f14.c'
OUT=G2/'build/c-firmware/20261016/main-text-stream-finish'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stddef.h>\n#include <stdint.h>\nsize_t strlen(const char*s){(void)s;return 0;}\nchar*strncpy(char*d,const char*s,size_t n){(void)s;(void)n;return d;}\nuint32_t audio_text_stream_buffer_create_553338(void*a,void**b,uint32_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}\nvoid audio_text_stream_schedule_552f6a(void*a,uint32_t b){(void)a;(void)b;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,present,target,source,total,notify,capacity_ok,callback):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 obj=0x20003000;dst=0x20004000;src=0x20005000;cb=0x100800
 seed=bytearray([0xa5]*0x30)
 for off,value in ((0,dst),(4,src),(0x0c,9),(0x10,total),(0x18,cb|1 if callback else 0),(0x24,64)):
  seed[off:off+4]=value.to_bytes(4,'little')
 cpu.mem_write(obj,bytes(seed));cpu.mem_write(dst,target+b'\0');cpu.mem_write(src,source+b'\0')
 cpu.reg_write(UC_ARM_REG_R0,obj if present else 0);cpu.reg_write(UC_ARM_REG_R1,0x12345678);cpu.reg_write(UC_ARM_REG_R2,notify)
 cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x44a43c:'strlen',0x44b5a0:'copy',0x553338:'capacity',0x552f6a:'schedule',cb:'callback'}
 names={'strlen':'strlen','strncpy':'copy','audio_text_stream_buffer_create_553338':'capacity','audio_text_stream_schedule_552f6a':'schedule'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock
 hooks[cb]='callback';calls=[]
 def readstr(machine,p):
  out=bytearray();i=0
  while (c:=machine.mem_read(p+i,1)[0])!=0:out.append(c);i+=1
  return bytes(out)
 def hook(machine,pc,width,unused):
  kind=hooks.get(pc)
  if kind is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if kind=='strlen':result=len(readstr(machine,a));calls.append(('strlen',a,result))
  elif kind=='capacity':result=int(capacity_ok);calls.append(('capacity',a,b,c,d))
  elif kind=='copy':
   data=readstr(machine,b)[:c];data+=b'\0'*(c-len(data));machine.mem_write(a,data);result=a;calls.append(('copy',a,b,c))
  elif kind=='schedule':result=0;calls.append(('schedule',a,b))
  else:result=0;calls.append(('callback',a))
  machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_text_stream_finish_552f14'] if compiled else 0x552f14
 cpu.emu_start(entry|1,0x600000,count=1000)
 return bytes(cpu.mem_read(obj,0x30)),bytes(cpu.mem_read(dst,32)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'finish-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'finish-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_text_stream_finish_552f14',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for present in (False,True):
  for target in (b'',b'a',b'ab',b'abcde'):
   for source in (b'',b'XYZ',b'abcdef'):
    for total in (0,1,2,5,0x80000000):
     for notify in (0,1,257):
      for capacity_ok in (False,True):
       for callback in (False,True):
        args=(present,target,source,total,notify,capacity_ok,callback)
        stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
        if stock!=actual:raise RuntimeError(f'finish mismatch {args}: {stock!r} != {actual!r}')
        cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_TEXT_STREAM_FINISH_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Null object, length, capacity, bounded copy, callback and schedule decisions','limits':['Lower-call side effects and whole-image behavior remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
