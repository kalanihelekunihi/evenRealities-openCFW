#!/usr/bin/env python3
"""Compare stock and C head-up setting routes and calibration UI state."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/setting_type4_head_up_466f28.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x466f28-BASE:0x467134-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-setting-type4-head-up-466f28'
HOOKS={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
       'compressed_log_output':0x43ce9e,
       'audio_settings_get_config_46b44c':0x46b44c,
       'audio_uart_service_mode':0x45a570,
       'audio_system_alert_close_464c36':0x464c36,
       'audio_uart_master_display_start':0x464b2e,
       'audio_settings_notify_recalibration_status_49beac':0x49beac,
       'audio_setting_head_up_configure_46c524':0x46c524}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\nuint8_t test_config[0x50];\n'
                  'uint8_t audio_uart_calibration_status_2007501c;\n'+''.join(
   f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_setting_dispatch_type4_466f28',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,kind,value,status,role,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   config=symbols['test_config'] if compiled else 0x20072da8
   status_cell=symbols['audio_uart_calibration_status_2007501c'] if compiled else 0x2007501c
   uc.mem_write(config,bytes([0xa5])*0x50);uc.mem_write(status_cell,bytes([status]))
   data=0x20010000
   if kind is not None:uc.mem_write(data,kind.to_bytes(2,'little')+b'\xa5\xa5'+u32(value))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,0 if kind is None else data)
   hooks={((symbols[name]&~1) if compiled else address):name for name,address in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    if name=='audio_log_flags':trace.append(('flags',));result=flags
    elif name=='audio_log_extended':trace.append(('extended',arg));result=0
    elif name=='compressed_log_output':trace.append(('short',arg));result=0
    elif name=='audio_settings_get_config_46b44c':trace.append(('config',));result=config
    elif name=='audio_uart_service_mode':trace.append(('role',));result=role
    elif name=='audio_system_alert_close_464c36':trace.append(('close',arg));result=0
    elif name=='audio_uart_master_display_start':trace.append(('start',arg));result=0
    elif name=='audio_settings_notify_recalibration_status_49beac':trace.append(('notify',arg));result=0
    else:trace.append(('apply',));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_setting_dispatch_type4_466f28'] if compiled else 0x466f28
   uc.emu_start(start|1,0x600000,count=850)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,kind,value,status,role,flags))
   return bytes(uc.mem_read(config,0x50)),uc.mem_read(status_cell,1)[0],trace
  cases=0
  for kind in (None,0,1,2,3,4,0xffff):
   for value in (0,1,2,0xffffffff):
    for status in (0,1,2):
     for role in (0,1,0x101):
      for flags in (0,1,2,4,7):
       args=(kind,value,status,role,flags)
       native=run(False,*args);candidate=run(True,*args)
       if native!=candidate:raise AssertionError((args,native,candidate))
       cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_SETTING_TYPE4_HEAD_UP_466F28',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,
           'limits':['Logging, service mode, display calls, config getter, status notification and head-up config are controlled hooks; final placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
