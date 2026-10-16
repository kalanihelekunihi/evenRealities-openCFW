#!/usr/bin/env python3
"""Controlled stock/C comparison for audio queue facade and hardware wrapper."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_control_and_open_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-audio-app-control-and-open'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nint32_t audio_cmsis_queue_put(void*a,const void*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t audio_thread_flags_set(void*a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t audio_log_flags(void){return 0;}\nvoid audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\nuint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\nvoid*audio_app_hardware_core_59123a(uint32_t a,uint32_t b,uint32_t c,uint32_t d,void*e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,kind,arg,queue,thread,result,flags,hardware_result):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 ctx=sy['g2_audio_control_context_20003f98'] if compiled else 0x20003f98
 seed=bytearray([0x5a]*0x10);seed[8:12]=thread.to_bytes(4,'little');seed[12:16]=queue.to_bytes(4,'little');cpu.mem_write(ctx,bytes(seed))
 packet=0x20004000;cpu.mem_write(packet,bytes(range(12)))
 cpu.reg_write(UC_ARM_REG_R0,arg if kind=='hardware' else (packet if arg else 0))
 cpu.reg_write(UC_ARM_REG_R1,0x11223344);cpu.reg_write(UC_ARM_REG_R2,0x55667788);cpu.reg_write(UC_ARM_REG_R3,0x20005000)
 cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x449abe:'put',0x449238:'signal',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed',0x59123a:'core'}
 names={'audio_cmsis_queue_put':'put','audio_thread_flags_set':'signal','audio_log_flags':'flags','audio_log_extended':'extended','compressed_log_output':'compressed','audio_app_hardware_core_59123a':'core'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock;calls=[]
 def readstr(machine,p):
  out=bytearray();i=0
  while (c:=machine.mem_read(p+i,1)[0])!=0:out.append(c);i+=1
  return bytes(out)
 def hook(machine,pc,width,unused):
  which=hooks.get(pc)
  if which is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if which=='put':calls.append((which,a,bytes(machine.mem_read(b,12)),c,d));value=result
  elif which=='signal':calls.append((which,a,b));value=0
  elif which=='flags':calls.append((which,));value=flags
  elif which=='extended':calls.append((which,a,readstr(machine,b),readstr(machine,d)));value=0
  elif which=='compressed':calls.append((which,a,readstr(machine,b)));value=0
  else:
   extra=int.from_bytes(machine.mem_read(machine.reg_read(UC_ARM_REG_SP),4),'little')
   calls.append((which,a,b,c,d,extra));value=hardware_result
  machine.reg_write(UC_ARM_REG_R0,value);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 name='audio_app_hardware_open_591374' if kind=='hardware' else 'audio_app_control_packet_53c638'
 entry=sy[name] if compiled else (0x591374 if kind=='hardware' else 0x53c638)
 cpu.emu_start(entry|1,0x600000,count=1000)
 return bytes(cpu.mem_read(ctx,0x10)),calls,(cpu.reg_read(UC_ARM_REG_R0) if kind=='hardware' else 0)

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'control-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'control-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_app_control_packet_53c638',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for arg,queue,thread,result,flags in itertools.product((0,1),(0,0x20006000),(0,0x20007000),(0,1,0xffffffff),(0,1,2,4,7)):
  args=('packet',arg,queue,thread,result,flags,0)
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'control mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 for arg,hardware_result in itertools.product((0,1,0x12345678),(0,0x20008000)):
  args=('hardware',arg,0,0,0,0,hardware_result)
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'hardware wrapper mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_AUDIO_APP_CONTROL_AND_OPEN_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Queue packet, signal/log branches, context cells, and hardware-core fifth stack argument','limits':['CMSIS queue, thread signal, hardware core side effects and final RAM placement remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
