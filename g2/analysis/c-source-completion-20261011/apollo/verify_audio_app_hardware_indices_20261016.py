#!/usr/bin/env python3
"""Controlled stock/C comparison for audio hardware index and zero helpers."""
import hashlib,json,subprocess,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_hardware_indices_20261016.c'
OUT=G2/'build/c-firmware/20261016/main-audio-app-hardware-indices'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,name,arg0,arg1):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload);cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
 for a,b in segments:cpu.mem_write(a,b)
 addr=0x20004000;cpu.mem_write(addr,b'Z'*128)
 cpu.reg_write(UC_ARM_REG_R0,addr if name=='audio_app_zero_tail_4d4ccc' else arg0)
 cpu.reg_write(UC_ARM_REG_R1,arg1);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
 stock={'audio_app_rate_index_590d3c':0x590d3c,'audio_app_format_index_590d74':0x590d74,'audio_app_zero_tail_4d4ccc':0x4d4ccc}
 entry=sy[name] if compiled else stock[name]
 cpu.emu_start(entry|1,0x600000,count=1000)
 return cpu.reg_read(UC_ARM_REG_R0) if name!='audio_app_zero_tail_4d4ccc' else bytes(cpu.mem_read(addr,128))

def main():
 payload=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
 OUT.mkdir(parents=True,exist_ok=True)
 stub=OUT/'indices-oracle-stub.c';stub.write_text('#include <stdint.h>\nvoid audio_uart_buffer_zero(void*p,uint32_t n,uint32_t fill){uint8_t*b=p;for(uint32_t i=0;i<n;++i)b[i]=(uint8_t)fill;}\n')
 elf_path=OUT/'indices-oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_app_rate_index_590d3c',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
 with elf_path.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 rates=(0,1,2500,5000,7500,8000,10000,16000,24000,32000,48000,96000,0xffffffff)
 for name in ('audio_app_rate_index_590d3c','audio_app_format_index_590d74'):
  for arg0,arg1 in itertools.product(rates,(0,1,2,0xffffffff)):
   stock=run(payload,segments,sy,False,name,arg0,arg1);actual=run(payload,segments,sy,True,name,arg0,arg1)
   if stock!=actual:raise RuntimeError(f'index mismatch {(name,arg0,arg1)}: {stock!r} != {actual!r}')
   cases+=1
 for length in (0,1,2,3,7,15,16,31,64,127):
  name='audio_app_zero_tail_4d4ccc';stock=run(payload,segments,sy,False,name,0,length);actual=run(payload,segments,sy,True,name,0,length)
  if stock!=actual:raise RuntimeError(f'zero mismatch {length}: {stock!r} != {actual!r}')
  cases+=1
 receipt={'status':'PASS_EXPERIMENTAL_AUDIO_APP_HARDWARE_INDICES_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Stock rate and format index tables plus zero-tail bytes for bounded lengths','limits':['Full descriptor hardware operation and final RAM placement remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
