#!/usr/bin/env python3
"""Compare stock and C head-up configuration with controlled HUB calls."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/setting_head_up_configure_46c524.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x46c524-BASE:0x46c5f2-BASE]).hexdigest()
PARAM_SHA=hashlib.sha256(IMAGE[0x78e654-BASE:0x78e65c-BASE]).hexdigest()
assert IMAGE[0x78e654-BASE:0x78e65c-BASE]==b'\0'*8
OUT=G2/'build/c-firmware/20261016/main-setting-head-up-configure-46c524'
HOOKS={'audio_uart_device_role_get':0x45a568,'audio_log_flags':0x43d0ce,
       'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,
       'audio_hub_channel_open':0x4a6d58,'audio_hub_channel_close':0x4a6dca,
       'audio_hub_parameter_config_4a6e3c':0x4a6e3c}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shim=Path(tmp)/'shim.c'
  shim.write_text('#include <stdint.h>\nuint8_t audio_settings_config_live[0x50];\n'
                  'uint8_t *audio_settings_config_previous;\n'+''.join(
   f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n' for name in HOOKS))
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_setting_head_up_configure_46c524',
                  str(SOURCE),str(shim),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,role,live_flag,live_switch,prior_switch,left,right,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   live=symbols['audio_settings_config_live'] if compiled else 0x20072da8
   prior=0x20010000
   pointer=symbols['audio_settings_config_previous'] if compiled else 0x20003700
   uc.mem_write(live,b'\xa5'*0x50);uc.mem_write(prior,b'\xa5'*0x50)
   uc.mem_write(live,bytes([live_flag]));uc.mem_write(live+0xa,bytes([live_switch]))
   uc.mem_write(prior+0xa,bytes([prior_switch]))
   for cell in (live,prior):
    uc.mem_write(cell+0xc,u32(left));uc.mem_write(cell+0x10,u32(right))
   uc.mem_write(pointer,u32(prior))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[name]&~1) if compiled else address):name for name,address in HOOKS.items()}
   trace=[]
   def observe(cpu,address,size,_):
    name=hooks.get(address)
    if name is None:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    if name=='audio_uart_device_role_get':trace.append(('role',));result=role
    elif name=='audio_log_flags':trace.append(('flags',));result=flags
    elif name=='audio_log_extended':trace.append(('extended',arg));result=0
    elif name=='compressed_log_output':trace.append(('short',arg));result=0
    elif name=='audio_hub_channel_open':trace.append(('open',arg));result=0
    elif name=='audio_hub_channel_close':trace.append(('close',arg));result=0
    else:
     param=cpu.reg_read(A.UC_ARM_REG_R1)
     words=tuple(int.from_bytes(cpu.mem_read(param+i,4),'little') for i in (0,4))
     trace.append(('parameter',arg,words));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols['audio_setting_head_up_configure_46c524'] if compiled else 0x46c524
   uc.emu_start(start|1,0x600000,count=450)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled,role,live_flag))
   return trace
  cases=0
  for role in (0,1,2):
   for live_flag in (0,1):
    for live_switch in (0,1,2):
     for prior_switch in (0,1):
      for left,right in ((0,0),(89,1),(90,1),(-90,0),(-91,0),
                         (0x7fffffff,1),(0x80000000,0xffffffff)):
       for flags in (0,1,2,4,7):
        args=(role,live_flag,live_switch,prior_switch,left,right,flags)
        native=run(False,*args);candidate=run(True,*args)
        if native!=candidate:raise AssertionError((args,native,candidate))
        cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_SETTING_HEAD_UP_CONFIGURE_46C524',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'parameter_template_sha256':PARAM_SHA,'cases':cases,
           'limits':['Role getter, logging and HUB operations are controlled hooks; HUB parameter configuration, final layout and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
