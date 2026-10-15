#!/usr/bin/env python3
"""Native/C child-call contract for Apollo 0x597446."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-record-status-read-round944';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_record_status_read.c'
obj=out/'td_record_status_read.o'
base=root/'build/c-firmware/td-state-alias-round943/apollo-main-td-state-alias.o'
linked=out/'apollo-main-td-record-status-read.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597446-0x438000:0x597452-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_td_counter_b_get(void){return 0;}
uint8_t audio_td_record_status_for_session(uint32_t x){(void)x;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_record_status_read',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,session,status):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  hooks={(syms['audio_td_counter_b_get'] if compiled else 0x5973dc)&~1:'counter',(syms['audio_td_record_status_for_session'] if compiled else 0x5973e4)&~1:'status'}
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   calls.append((name,cpu.reg_read(A.UC_ARM_REG_R0) if name=='status' else None))
   cpu.reg_write(A.UC_ARM_REG_R0,session if name=='counter' else status)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0xdeadbeef),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_td_record_status_read'] if compiled else 0x597446)|1),0x600000,count=100)
  return uc.reg_read(A.UC_ARM_REG_R0)&255,tuple(calls)
 cases=[]
 for session in (0,1,0x12345678,0xffffffff):
  for status in (0,1,2,3,255):
   n=run(False,session,status);c=run(True,session,status)
   assert n==c,(session,status,n,c)
   cases.append((session,status))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_record_status_read'}
assert after-before=={'audio_td_record_status_for_session'}
receipt={'round':944,'status':'PASS_NATIVE_TD_RECORD_STATUS_READ','component':'Apollo record status wrapper 0x597446','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C child call order, session argument, low-byte result','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Session status lookup 0x5973e4 and candidate session selector 0x5e505a remain open','Final RAM placement/initialization and callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
