#!/usr/bin/env python3
"""Controlled stock/C comparison for ANCC clear and remote sync."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_sync_remote_4973f4.c'
OUT=G2/'build/c-firmware/20261016/main-even-ai-sync-remote'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nvoid*audio_settings_ancc_mutex;\nuint8_t audio_settings_ancc_count;\nint32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}\nint32_t audio_file_mutex_release(void*a){(void)a;return 0;}\nvoid audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nuint32_t audio_log_flags(void){return 0;}\nvoid audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\nuint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\nvoid audio_even_ai_ancc_display_clear_4e1af8(uint32_t a,uint32_t b){(void)a;(void)b;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,mutex,lock_result,notify,flags):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x200000)
 for a,b in segments:cpu.mem_write(a,b)
 addrs={'records':sy['g2_audio_ancc_records_20104c54'] if compiled else 0x20104c54,'seq':sy['g2_audio_ancc_sequence_20074918'] if compiled else 0x20074918,'mutex':sy['audio_settings_ancc_mutex'] if compiled else 0x2007491c,'count':sy['audio_settings_ancc_count'] if compiled else 0x2007500d}
 cpu.mem_write(addrs['records'],b'Z'*0x1e28);cpu.mem_write(addrs['seq'],(0x12345678).to_bytes(4,'little'))
 cpu.mem_write(addrs['mutex'],(0x20005000 if mutex else 0).to_bytes(4,'little'));cpu.mem_write(addrs['count'],b'\x7f')
 cpu.reg_write(UC_ARM_REG_R0,notify);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x4497b6:'lock',0x44981c:'unlock',0x43c0e4:'zero',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed',0x4e1af8:'display'}
 names={'audio_file_mutex_acquire':'lock','audio_file_mutex_release':'unlock','audio_uart_buffer_zero':'zero','audio_log_flags':'flags','audio_log_extended':'extended','compressed_log_output':'compressed','audio_even_ai_ancc_display_clear_4e1af8':'display'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock;calls=[]
 def readstr(machine,p):
  out=bytearray();i=0
  while (c:=machine.mem_read(p+i,1)[0])!=0:out.append(c);i+=1
  return bytes(out)
 def hook(machine,pc,width,unused):
  kind=hooks.get(pc)
  if kind is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if kind=='lock':calls.append((kind,a,b));result=lock_result
  elif kind=='zero':machine.mem_write(a,bytes([c&255])*b);calls.append((kind,a==addrs['records'],b,c));result=0
  elif kind=='flags':calls.append((kind,));result=flags
  elif kind=='extended':calls.append((kind,a,readstr(machine,b),readstr(machine,d)));result=0
  elif kind=='compressed':calls.append((kind,a,readstr(machine,b)));result=0
  elif kind=='display':calls.append((kind,a,b));result=0
  else:calls.append((kind,a));result=0
  machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_even_ai_sync_remote_4973f4'] if compiled else 0x4973f4
 cpu.emu_start(entry|1,0x600000,count=1000)
 return bytes(cpu.mem_read(addrs['records'],0x1e28)),bytes(cpu.mem_read(addrs['seq'],4)),bytes(cpu.mem_read(addrs['count'],1)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'sync-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'sync-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_even_ai_sync_remote_4973f4',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for args in itertools.product((False,True),(0,1),(0,1,257),(0,1,2,4,7)):
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'sync mismatch {args}: {stock[-1]!r} != {actual[-1]!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_EVEN_AI_SYNC_REMOTE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Mutex and log branches, 0x1e28-byte clear, sequence/count reset, display child call','limits':['ANCC record extent beyond observed clear and final RAM placement remain open; no hardware proof.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
