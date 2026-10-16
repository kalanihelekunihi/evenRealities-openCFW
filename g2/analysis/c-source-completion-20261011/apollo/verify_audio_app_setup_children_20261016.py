#!/usr/bin/env python3
"""Controlled stock/C comparison for first-app setup descendants."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_setup_children_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-audio-app-setup-children'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\nvoid audio_app_control_packet_53c638(const void*a){(void)a;}\nvoid*audio_app_hardware_open_591374(uint32_t a,uint32_t b,uint32_t c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,name,arg,seed,handle):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 context=0x20003000;cpu.mem_write(context,seed)
 cpu.reg_write(UC_ARM_REG_R0,arg);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={'audio_app_stream_enable_53ca10':0x53ca10,'audio_app_codec_enable_53ca32':0x53ca32,'audio_app_first_hardware_prepare_57a926':0x57a926}
 child=(sy['audio_app_control_packet_53c638']&~1 if compiled else 0x53c638) if name!='audio_app_first_hardware_prepare_57a926' else (sy['audio_app_hardware_open_591374']&~1 if compiled else 0x591374)
 calls=[]
 def hook(machine,pc,width,unused):
  if pc!=child:return
  a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
  if name=='audio_app_first_hardware_prepare_57a926':calls.append((a,b,c,d-context));result=handle
  else:calls.append(bytes(machine.mem_read(a,12)));result=0
  machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=sy[name] if compiled else stock[name]
 cpu.emu_start(entry|1,0x600000,count=300)
 return bytes(cpu.mem_read(context,0x20)),calls

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True);stub=OUT/'children-oracle-stub.c';stub.write_text(STUB)
 elf_path=OUT/'children-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_app_stream_enable_53ca10',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name in ('audio_app_stream_enable_53ca10','audio_app_codec_enable_53ca32'):
  for arg in (0,1,2,255,256,257,0xffffffff):
   seed=bytes([0x5a]*0x20);stock=run(payload,segments,sy,False,name,arg,seed,0);actual=run(payload,segments,sy,True,name,arg,seed,0)
   if stock!=actual:raise RuntimeError(f'packet mismatch {name} {arg}: {stock!r} != {actual!r}')
   cases+=1
 name='audio_app_first_hardware_prepare_57a926'
 for arg in (0,0x20003000):
  for first in (0,1,0x12345678):
   for second in (0,2,0x87654321):
    for handle in (0,0x20007000):
     seed=bytearray([0x5a]*0x20);seed[4:8]=first.to_bytes(4,'little');seed[8:12]=second.to_bytes(4,'little')
     stock=run(payload,segments,sy,False,name,arg,bytes(seed),handle);actual=run(payload,segments,sy,True,name,arg,bytes(seed),handle)
     if stock!=actual:raise RuntimeError(f'hardware mismatch {(arg,first,second,handle)}: {stock!r} != {actual!r}')
     cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_AUDIO_APP_SETUP_CHILDREN_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Two 12-byte control packets and hardware context access/write through +0x1f','limits':['Control packet and hardware-open child side effects; final RAM placement remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
