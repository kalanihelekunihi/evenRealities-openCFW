#!/usr/bin/env python3
"""Compare stock and C ALS manual target branch, arithmetic and cell writes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_manual_target_4ade36.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4ade36-0x438000:0x4adec4-0x438000]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-als-manual-target-4ade36'
HOOKS={'audio_als_first_curve_percent_4ad9e2':0x4ad9e2,
       'audio_als_manual_target_scale_4addb6':0x4addb6}
CELLS={'audio_als_curve_nominal':0x200741e8,
       'audio_als_scale_active':0x20000064,
       'audio_als_scale_shadow':0x20000068,
       'audio_als_recompute_pending':0x20074200,
       'audio_als_manual_target_count':0x200741fc}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\n'+''.join(
   f'uint32_t {name};\n' for name in CELLS if name!='audio_als_manual_target_count')+
   ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_als_manual_set_target_4ade36',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,level,nominal,active,target):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   values={'audio_als_curve_nominal':nominal,'audio_als_scale_active':active,
           'audio_als_scale_shadow':0xa1a1a1a1,'audio_als_recompute_pending':0xb2b2b2b2,
           'audio_als_manual_target_count':7}
   for name,value in values.items():uc.mem_write(symbols[name] if compiled else CELLS[name],u32(value))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,level)
   hooks={((symbols[name]&~1) if compiled else addr):name for name,addr in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    if name=='audio_als_first_curve_percent_4ad9e2':
     trace.append(('curve',)); result=35
    else:
     trace.append(('target',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
     result=target
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_als_manual_set_target_4ade36'] if compiled else 0x4ade36
   uc.emu_start(start|1,0x600000,count=220)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,level))
   cells=tuple(int.from_bytes(uc.mem_read(symbols[name] if compiled else CELLS[name],4),'little')
               for name in CELLS)
   return cells,trace
  cases=0
  for level in (0,2,50,100,0xffffffff):
   for nominal in (0,34,35,36,100):
    for active in (0,614,1024,1434,0xffffffff):
     for target in (0,614,1024,1434,0xffffffff):
      args=(level,nominal,active,target)
      native=run(False,*args);candidate=run(True,*args)
      if native!=candidate:raise AssertionError((args,native,candidate))
      cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_ALS_MANUAL_TARGET_4ADE36',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,'limits':['Curve getter and target-scale child are controlled hooks; final RAM placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
