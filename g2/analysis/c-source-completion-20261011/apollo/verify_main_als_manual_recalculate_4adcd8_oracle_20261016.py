#!/usr/bin/env python3
"""Compare stock and C ALS learning reset across observed cells and fill call."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_manual_recalculate_4adcd8.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4adcd8-0x438000:0x4add02-0x438000]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-als-manual-recalculate-4adcd8'
CELLS={'audio_als_manual_accumulator':0x200741cc,
       'audio_als_manual_sample':0x200741c8,
       'audio_als_active_previous':0x200741e0,
       'audio_als_manual_window':0x20073c98}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\nuint32_t audio_als_active_previous;\n'
                  '__attribute__((naked)) void audio_uart_buffer_zero(void){__asm volatile("bx lr");}\n')
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_als_manual_recalculate_4adcd8',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,a,b,previous,fill):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   def cell(name):return symbols[name] if compiled else CELLS[name]
   uc.mem_write(cell('audio_als_manual_accumulator'),u32(a))
   uc.mem_write(cell('audio_als_manual_sample'),u32(b))
   uc.mem_write(cell('audio_als_active_previous'),u32(previous))
   uc.mem_write(cell('audio_als_manual_window'),bytes([fill])*20)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   calls=[]
   fill_address=(symbols['audio_uart_buffer_zero']&~1) if compiled else 0x43c0e4
   def observe(cpu,address,size,_):
    if address!=fill_address:return
    dest=cpu.reg_read(A.UC_ARM_REG_R0)
    length=cpu.reg_read(A.UC_ARM_REG_R1)
    value=cpu.reg_read(A.UC_ARM_REG_R2)
    calls.append((dest==cell('audio_als_manual_window'),length,value))
    if length<=20:cpu.mem_write(dest,bytes([value&255])*length)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_als_manual_recalculate_4adcd8'] if compiled else 0x4adcd8
   uc.emu_start(start|1,0x600000,count=120)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled))
   cells=tuple(int.from_bytes(uc.mem_read(cell(name),4),'little') for name in
               ('audio_als_manual_accumulator','audio_als_manual_sample','audio_als_active_previous'))
   window=bytes(uc.mem_read(cell('audio_als_manual_window'),20))
   return cells,window,calls
  cases=0
  for a in (0,0x12345678,0xffffffff):
   for b in (0,0xa5a5a5a5,0xffffffff):
    for previous in (0,1,0xffffffff):
     for fill in (0,0x5a,0xff):
      args=(a,b,previous,fill);native=run(False,*args);candidate=run(True,*args)
      if native!=candidate:raise AssertionError((args,native,candidate))
      cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_ALS_MANUAL_RECALCULATE_4ADCD8',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,'limits':['Native fill helper is an observed controlled hook; final RAM placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
