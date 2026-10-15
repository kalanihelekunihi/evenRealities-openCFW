#!/usr/bin/env python3
"""Compare Apollo 0x5e50ea with its C mapper at child-call boundaries."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-runtime-mapper-round942';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_runtime_event_from_ble.c'
obj=out/'terminal_runtime_event_from_ble.o'
base=root/'build/c-firmware/terminal-runtime-event-round941/apollo-main-terminal-runtime-event.o'
linked=out/'apollo-main-terminal-runtime-mapper.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e50ea-0x438000:0x5e5166-0x438000]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_terminal_runtime_saved_session;
uint8_t *audio_td_state_ptr_alias1(void){return (uint8_t *)0;}
uint8_t *audio_td_session_struct_ptr(void){return (uint8_t *)0;}
uint32_t audio_terminal_candidate_session_for_runtime(void){return 0;}
uint8_t audio_td_record_status_read(void){return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_runtime_event_from_ble',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'state':'audio_td_state_ptr_alias1','session':'audio_td_session_struct_ptr','candidate':'audio_terminal_candidate_session_for_runtime','status':'audio_td_record_status_read'}
 native_addrs={'state':0x597344,'session':0x59731e,'candidate':0x5e505a,'status':0x597446}
 def run(compiled,ble,host,session_present,session_flag,candidate,status,saved):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  state=0x2010fd20;session=state+0x808
  uc.mem_write(state+0xa1d8,bytes([host]))
  uc.mem_write(session+0x406,session_flag.to_bytes(2,'little'))
  saved_addr=syms['audio_terminal_runtime_saved_session'] if compiled else 0x2006e358
  uc.mem_write(saved_addr,saved.to_bytes(4,'little'))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   calls.append(name)
   value={'state':state,'session':session if session_present else 0,'candidate':candidate,'status':status}[name]
   cpu.reg_write(A.UC_ARM_REG_R0,value)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,ble),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_runtime_event_from_ble'] if compiled else 0x5e50ea)|1),0x600000,count=500)
  return (uc.reg_read(A.UC_ARM_REG_R0),tuple(calls),int.from_bytes(uc.mem_read(saved_addr,4),'little'))
 cases=[]
 for ble in (0,1,255):
  for host in (0,1,2,3,255):
   for session_present in (False,True):
    for session_flag in (0,1,0x100):
     for candidate in (0,0x12345678):
      for status in (0,1,2,3,255):
       args=(ble,host,session_present,session_flag,candidate,status,0xabcdef)
       n=run(False,*args);c=run(True,*args)
       assert n==c,(args,n,c)
       cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_runtime_event_from_ble'}
assert after-before=={'audio_td_state_ptr_alias1','audio_terminal_candidate_session_for_runtime','audio_td_record_status_read'}
receipt={'round':942,'status':'PASS_NATIVE_TERMINAL_RUNTIME_MAPPER','component':'Apollo terminal runtime-event mapper 0x5e50ea','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C child call order, event result and saved-session RAM cell','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Candidate session selector 0x5e505a and record status reader 0x597446 remain open','Final linker placement and RAM initialization remain open','5 terminal callback bodies and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
