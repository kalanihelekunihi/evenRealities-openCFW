#!/usr/bin/env python3
"""Controlled stock/C comparison for audio hardware descriptor builder."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_hardware_core_59123a.c'
OUT=G2/'build/c-firmware/20261016/main-audio-app-hardware-core'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nint32_t audio_app_rate_index_590d3c(int32_t a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t audio_app_format_index_590d74(int32_t a,uint32_t b){(void)a;(void)b;return 0;}\nvoid audio_uart_lv_memzero_48949c(void*a,uint32_t b){(void)a;(void)b;}\nvoid*audio_uart_display_area_copy_439c04(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}\nvoid audio_app_zero_tail_4d4ccc(void*a,uint32_t b){(void)a;(void)b;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,format,rate,first,last,rate_idx,first_idx,last_idx,present):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 out=0x20008000;cpu.mem_write(out,b'Z'*0x4b0)
 cpu.reg_write(UC_ARM_REG_R0,format);cpu.reg_write(UC_ARM_REG_R1,rate);cpu.reg_write(UC_ARM_REG_R2,first);cpu.reg_write(UC_ARM_REG_R3,last)
 sp=0x200ff000;cpu.reg_write(UC_ARM_REG_SP,sp);cpu.mem_write(sp,(out if present else 0).to_bytes(4,'little'));cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={0x590d3c:'rate_idx',0x590d74:'format_idx',0x48949c:'zero',0x439c04:'copy',0x4d4ccc:'tail'}
 names={'audio_app_rate_index_590d3c':'rate_idx','audio_app_format_index_590d74':'format_idx','audio_uart_lv_memzero_48949c':'zero','audio_uart_display_area_copy_439c04':'copy','audio_app_zero_tail_4d4ccc':'tail'}
 hooks={sy[k]&~1:v for k,v in names.items()} if compiled else stock;calls=[];format_calls=0
 def hook(machine,pc,width,unused):
  nonlocal format_calls
  kind=hooks.get(pc)
  if kind is None:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2)
  if kind=='rate_idx':calls.append((kind,a,b));value=rate_idx
  elif kind=='format_idx':calls.append((kind,a,b));value=first_idx if format_calls==0 else last_idx;format_calls+=1
  elif kind=='zero':machine.mem_write(a,b'\0'*b);calls.append((kind,b));value=0
  elif kind=='copy':machine.mem_write(a,bytes(machine.mem_read(b,c)));calls.append((kind,c));value=a
  else:calls.append((kind,a-out,b));value=0
  machine.reg_write(UC_ARM_REG_R0,value);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_app_hardware_core_59123a'] if compiled else 0x59123a
 cpu.emu_start(entry|1,0x600000,count=1000)
 return cpu.reg_read(UC_ARM_REG_R0),bytes(cpu.mem_read(out,0x4b0)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'hardware-core-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'hardware-core-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_app_hardware_core_59123a',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for format,rate,first,last,rate_idx,first_idx,last_idx,present in itertools.product((0,1),(7500,1250,44100),(1,2),(0,2,5),(0,2,4),(0,2),(0,2,6,7),(False,True)):
  args=(format,rate,first,last,rate_idx,first_idx,last_idx,present)
  stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
  if stock!=actual:raise RuntimeError(f'hardware core mismatch {args}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_AUDIO_APP_HARDWARE_CORE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Index gates, descriptor fields, 0x4b0-byte copy, fixed-point tail length, fifth stack argument','limits':['Index helpers and tail-zero lower-call side effects remain open; no device proof.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
