#!/usr/bin/env python3
"""Compare stock and C IMU acceleration interval configuration."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/hub_imu_accel_config_4a52a2.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x4a52a2-BASE:0x4a5308-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-hub-imu-accel-config-4a52a2'
HOOKS={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
       'compressed_log_output':0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\n'+''.join(
   f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_hub_imu_accel_config_4a52a2',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,interval,flags,previous):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   cell=symbols['audio_hub_imu_report_interval_cell'] if compiled else 0x20000e60
   uc.mem_write(cell,u32(previous))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,interval)
   hooks={((symbols[name]&~1) if compiled else address):name for name,address in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    if name=='audio_log_flags':trace.append(('flags',));result=flags
    elif name=='audio_log_extended':trace.append(('extended',arg));result=0
    else:trace.append(('short',arg));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_hub_imu_accel_config_4a52a2'] if compiled else 0x4a52a2
   uc.emu_start(start|1,0x600000,count=150)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,interval))
   return uc.reg_read(A.UC_ARM_REG_R0),int.from_bytes(uc.mem_read(cell,4),'little'),trace
  cases=0
  for interval in (0,99,100,101,4999,5000,5001,0xffffffff):
   for flags in (0,1,2,4,7):
    for previous in (0,0xa5a5a5a5):
     args=(interval,flags,previous)
     native=run(False,*args);candidate=run(True,*args)
     if native!=candidate:raise AssertionError((args,native,candidate))
     cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_HUB_IMU_ACCEL_CONFIG_4A52A2',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,
           'limits':['Logging calls are controlled hooks; final RAM placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
