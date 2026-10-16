#!/usr/bin/env python3
"""Controlled stock/C comparison for the text-stream begin wrapper."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_begin_552f0a.c'
OUT=G2/'build/c-firmware/20261016/main-text-stream-begin'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,obj,notify):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 cpu.reg_write(UC_ARM_REG_R0,obj);cpu.reg_write(UC_ARM_REG_R1,notify);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 child=(sy['audio_text_stream_schedule_552f6a']&~1) if compiled else 0x552f6a
 calls=[]
 def hook(machine,pc,width,unused):
  if pc!=child:return
  calls.append((machine.reg_read(UC_ARM_REG_R0),machine.reg_read(UC_ARM_REG_R1)))
  machine.reg_write(UC_ARM_REG_R0,0xdeadbeef);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy['audio_text_stream_begin_552f0a'] if compiled else 0x552f0a
 cpu.emu_start(entry|1,0x600000,count=100)
 return calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True)
 stub=OUT/'begin-oracle-stub.c';stub.write_text('#include <stdint.h>\nvoid audio_text_stream_schedule_552f6a(void*a,uint32_t b){(void)a;(void)b;}\n')
 elf_path=OUT/'begin-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_text_stream_begin_552f0a',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for obj in (0,0x20003000,0xffffffff):
  for notify in (0,1,255,256,257,0xffffffff):
   args=(obj,notify);stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
   if stock!=actual:raise RuntimeError(f'begin mismatch {args}: {stock} != {actual}')
   cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_TEXT_STREAM_BEGIN_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Wrapper child call and notify byte narrowing','limits':['Child schedule behavior remains open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
