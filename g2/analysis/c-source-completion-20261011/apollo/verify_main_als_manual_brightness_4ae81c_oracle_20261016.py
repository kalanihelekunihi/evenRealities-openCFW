#!/usr/bin/env python3
"""Compare the stock ALS manual learner with its bounded C body."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]; G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_manual_brightness_4ae81c.c'
STATE=G2/'components/audio/uart_thread_source_candidate/display_als_state.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4ae81c-0x438000:0x4ae8d2-0x438000]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-als-manual-brightness-4ae81c'
HOOKS={'audio_als_apply_previous':0x4add8c,
       'audio_als_manual_set_target_4ade36':0x4ade36,
       'audio_als_manual_recalculate_4adcd8':0x4adcd8,
       'audio_log_flags':0x43d0ce,
       'audio_log_extended':0x43d574,
       'compressed_log_output':0x43ce9e}
CELLS={'audio_als_manual_ready':0x200741c0,
       'audio_als_active_previous':0x200741e0,
       'audio_als_default_previous':0x200741dc,
       'audio_als_manual_level':0x200741f0,
       'audio_als_manual_level_copy':0x200741f4,
       'audio_als_manual_pending':0x200741f8,
       'audio_als_scale_active':0x20000064,
       'audio_als_curve_adjusted':0x200741ec}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\n'+ '\n'.join(
      f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}'
      for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_als_manual_set_brightness_4ae81c',
                  str(SOURCE),str(STATE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,level,ready,active,default,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   values={'audio_als_manual_ready':ready,'audio_als_active_previous':active,
           'audio_als_default_previous':default,'audio_als_manual_level':0xa1a1a1a1,
           'audio_als_manual_level_copy':0xb2b2b2b2,'audio_als_manual_pending':0xc3c3c3c3,
           'audio_als_scale_active':0x401,'audio_als_curve_adjusted':67}
   for name,value in values.items():
    uc.mem_write(symbols[name] if compiled else CELLS[name],u32(value))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,level)
   hooks={((symbols[name]&~1) if compiled else addr):name for name,addr in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    if name=='audio_log_flags':trace.append(('flags',)); result=flags
    elif name=='audio_als_apply_previous':trace.append(('apply',arg));result=0
    elif name=='audio_als_manual_set_target_4ade36':trace.append(('target',arg));result=0
    elif name=='audio_als_manual_recalculate_4adcd8':trace.append(('recalculate',));result=0
    elif name=='audio_log_extended':trace.append(('extended',arg));result=0
    else:trace.append(('short',arg));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_als_manual_set_brightness_4ae81c'] if compiled else 0x4ae81c
   uc.emu_start(start|1,0x600000,count=500)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:
    raise RuntimeError(('learner did not return',compiled,level,ready,flags))
   cells=tuple(int.from_bytes(uc.mem_read(symbols[name] if compiled else CELLS[name],4),'little')
               for name in ('audio_als_manual_level','audio_als_manual_level_copy','audio_als_manual_pending'))
   return uc.reg_read(A.UC_ARM_REG_R0),cells,trace
  cases=0
  for level in (0,1,2,3,99,100,101,0xffffffff):
   for ready in (0,1):
    for active,default in ((0,0),(0,0x123),(0x456,0x123)):
     for flags in (0,1,2,4,7):
      args=(level,ready,active,default,flags)
      native=run(False,*args);compiled=run(True,*args)
      if native!=compiled:raise AssertionError((args,native,compiled))
      cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_ALS_MANUAL_BRIGHTNESS_4AE81C',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'state_source_sha256':sha(STATE),'official_payload_sha256':IMAGE_SHA,
           'native_body_sha256':BODY_SHA,'cases':cases,
           'limits':['Three ALS helper calls are controlled hooks; final RAM placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
