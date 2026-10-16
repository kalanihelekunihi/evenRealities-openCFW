#!/usr/bin/env python3
"""Compare stock and C HUB parameter dispatch under controlled children."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/hub_parameter_config_4a6e3c.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x4a6e3c-BASE:0x4a6eca-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-hub-parameter-config-4a6e3c'
HOOKS={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
       'compressed_log_output':0x43ce9e,
       'audio_hub_semantic_motion_threshold_4a4e8c':0x4a4e8c,
       'audio_hub_semantic_motion_period_4a4ec0':0x4a4ec0,
       'audio_hub_imu_accel_config_4a52a2':0x4a52a2}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\nvolatile uint16_t audio_uart_hub_role_cell;\n'+''.join(
   f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_hub_parameter_config_4a6e3c',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,role,kind,first,second,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   cell=symbols['audio_uart_hub_role_cell'] if compiled else 0x20004526
   uc.mem_write(cell,role.to_bytes(2,'little'))
   params=0x20010000;uc.mem_write(params,u32(first)+u32(second))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,kind);uc.reg_write(A.UC_ARM_REG_R1,params)
   hooks={((symbols[name]&~1) if compiled else address):name for name,address in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    if name=='audio_log_flags':trace.append(('flags',));result=flags
    elif name=='audio_log_extended':trace.append(('extended',arg));result=0
    elif name=='compressed_log_output':trace.append(('short',arg));result=0
    elif name=='audio_hub_semantic_motion_threshold_4a4e8c':trace.append(('threshold',arg));result=0
    elif name=='audio_hub_semantic_motion_period_4a4ec0':
     trace.append(('period',arg,cpu.reg_read(A.UC_ARM_REG_R1)));result=0
    else:trace.append(('accel',arg));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_hub_parameter_config_4a6e3c'] if compiled else 0x4a6e3c
   uc.emu_start(start|1,0x600000,count=300)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,role,kind))
   return uc.reg_read(A.UC_ARM_REG_R0),trace
  cases=0
  for role in (0,2,3):
   for kind in (0,1,2,3,5,0x101,0x102,0x105,255):
    for first,second in ((0,0),(1,2),(0xffffffff,0x12345678)):
     for flags in (0,1,2,4,7):
      args=(role,kind,first,second,flags)
      native=run(False,*args);candidate=run(True,*args)
      if native!=candidate:raise AssertionError((args,native,candidate))
      cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_HUB_PARAMETER_CONFIG_4A6E3C',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,
           'limits':['Logging and three semantic or IMU children are controlled hooks; final layout and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
