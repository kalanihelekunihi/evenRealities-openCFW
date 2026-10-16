#!/usr/bin/env python3
"""Controlled stock/C comparison for audio manager app acquisition."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_app_acquire_54f380.c'
OUT=G2/'build/c-firmware/20261016/main-even-ai-app-acquire'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nuint8_t audio_uart_device_role_get(void){return 2;}\nuint32_t audio_log_flags(void){return 0;}\nvoid audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\nuint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\nvoid audio_app_first_hardware_prepare_57a926(const void*a){(void)a;}\nvoid audio_app_codec_enable_53ca32(uint32_t a){(void)a;}\nvoid audio_app_stream_enable_53ca10(uint32_t a){(void)a;}\nuint8_t g2_audio_first_hardware_context_20108948;\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,role,app,initial,flags):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 state=(sy['g2_audio_app_acquired'] if compiled else 0x20074180)
 cpu.mem_write(state,initial)
 cpu.reg_write(UC_ARM_REG_R0,app);cpu.reg_write(UC_ARM_REG_R1,0x11223344);cpu.reg_write(UC_ARM_REG_R2,0x55667788);cpu.reg_write(UC_ARM_REG_R3,0x99aabbcc)
 cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x45a568:'role',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed',0x57a926:'hardware',0x53ca32:'codec',0x53ca10:'stream'}
 names={'audio_uart_device_role_get':'role','audio_log_flags':'flags','audio_log_extended':'extended','compressed_log_output':'compressed','audio_app_first_hardware_prepare_57a926':'hardware','audio_app_codec_enable_53ca32':'codec','audio_app_stream_enable_53ca10':'stream'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock;calls=[]
 def readstr(machine,p):
  out=bytearray();i=0
  while (c:=machine.mem_read(p+i,1)[0])!=0:out.append(c);i+=1
  return bytes(out)
 def hook(machine,pc,width,unused):
  kind=hooks.get(pc)
  if kind is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if kind=='role':calls.append((kind,));result=role
  elif kind=='flags':calls.append((kind,));result=flags
  elif kind=='extended':calls.append((kind,a,readstr(machine,b),readstr(machine,d)));result=0
  elif kind=='compressed':calls.append((kind,a,readstr(machine,b)));result=0
  elif kind=='hardware':calls.append((kind,));result=0
  else:calls.append((kind,a));result=0
  machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_even_ai_app_acquire_54f380'] if compiled else 0x54f380
 cpu.emu_start(entry|1,0x600000,count=3000)
 return cpu.reg_read(UC_ARM_REG_R0),bytes(cpu.mem_read(state,8)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'app-acquire-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'app-acquire-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_even_ai_app_acquire_54f380',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 seeds=[b'\0'*8,bytes([0,1,0,0,0,0,0,0]),bytes([0,2,0,0,0,0,0,0]),bytes([1]*8)]
 for role,app,initial,flags in itertools.product((0,1,2,3),(0,1,2,7,8,255,257),seeds,(0,1,2,4,7)):
  args=(role,app,initial,flags);stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'app acquire mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_EVEN_AI_APP_ACQUIRE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Role and app guards, eight-byte acquisition state, count, logging flags and first-app lower-call order','limits':['First hardware context extent and placement, lower-call side effects and whole-image behavior remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
