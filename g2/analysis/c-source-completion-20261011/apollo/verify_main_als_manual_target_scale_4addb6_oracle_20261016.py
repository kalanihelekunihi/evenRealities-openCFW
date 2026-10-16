#!/usr/bin/env python3
"""Compare stock and C ALS target-scale arithmetic with controlled divide."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_manual_target_scale_4addb6.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x4addb6-BASE:0x4ade36-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-als-manual-target-scale-4addb6'
HOOKS={'audio_als_first_curve_percent_4ad9e2':0x4ad9e2,
       'audio_uart_ring_u64_div_47cc60':0x47cc60}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\n'+''.join(
   f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_als_manual_target_scale_4addb6',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,nominal,requested,divide_result):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,nominal);uc.reg_write(A.UC_ARM_REG_R1,requested)
   hooks={((symbols[name]&~1) if compiled else address):name for name,address in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    if name=='audio_als_first_curve_percent_4ad9e2':trace.append(('first',)); result=35
    else:
     regs=tuple(cpu.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                             A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
     trace.append(('divide',)+regs); result=divide_result
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_als_manual_target_scale_4addb6'] if compiled else 0x4addb6
   uc.emu_start(start|1,0x600000,count=220)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,nominal,requested))
   return uc.reg_read(A.UC_ARM_REG_R0),trace
  cases=0
  for nominal in (0,34,35,36,100,0xffffffff):
   for requested in (0,34,35,36,99,100,101,0xffffffff):
    for divide_result in (0,613,614,615,1433,1434,0xffffffff):
     args=(nominal,requested,divide_result)
     native=run(False,*args);candidate=run(True,*args)
     if native!=candidate:raise AssertionError((args,native,candidate))
     cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_ALS_MANUAL_TARGET_SCALE_4ADDB6',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,
           'limits':['The stock first-curve getter and 64-bit divide are controlled hooks; final layout and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
