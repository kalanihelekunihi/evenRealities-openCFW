#!/usr/bin/env python3
"""Native/C Apollo input-message sender queue and thread-flag contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/input-msg-record-round968';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/input_msg_send_record.c'
obj=out/'input_msg_send_record.o'
base=root/'build/c-firmware/input-msg-id4-round967/apollo-main-input-msg-id4.o'
linked=out/'apollo-main-input-msg-record.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x51301c-0x438000:0x513056-0x438000]
assert int.from_bytes(blob[0x5134b4-0x438000:0x5134b8-0x438000],'little')==0x2000408c
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_os_message_queue_put(uint32_t a,const void*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_os_thread_flags_set(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
void audio_input_error_log(const char*p){(void)p;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_input_message_send_record',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'queue':'audio_os_message_queue_put','flags':'audio_os_thread_flags_set','error':'audio_input_error_log'}
 native_addrs={'queue':0x449abe,'flags':0x449238,'error':0x4733ee}
 cases=[]
 for present in (False,True):
  for queue in (0,0x1234):
   for thread in (0,0x5678):
    for result in (0,1,0xffffffff):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
      uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      state=syms['audio_input_message_state'] if compiled else 0x2000408c
      record=0x20010000;uc.mem_write(record,bytes(range(16)))
      uc.mem_write(state+8,thread.to_bytes(4,'little'));uc.mem_write(state+12,queue.to_bytes(4,'little'))
      hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
      calls=[]
      def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
      def hook(cpu,address,size,user):
       name=hooks.get(address)
       if not name:return
       r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
       r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
       if name=='queue':calls.append((name,r0,r1-record,r2,r3,bytes(cpu.mem_read(r1,16))));cpu.reg_write(A.UC_ARM_REG_R0,result)
       elif name=='flags':calls.append((name,r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
       else:calls.append((name,string(r0)))
       cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
      uc.hook_add(UC_HOOK_CODE,hook)
      for reg,val in ((A.UC_ARM_REG_R0,record if present else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
      uc.emu_start(((syms['audio_input_message_send_record'] if compiled else 0x51301c)|1),0x600000,count=150)
      outputs.append(tuple(calls))
     assert outputs[0]==outputs[1],(present,queue,thread,result,outputs)
     cases.append((present,queue,thread,result))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_input_message_send_record'}
assert after-before=={'audio_os_message_queue_put','audio_os_thread_flags_set','audio_input_error_log'}
receipt={'round':968,'status':'PASS_NATIVE_INPUT_MSG_RECORD','component':'Apollo input_msg_send_record 0x51301c','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C null/queue gates, queue put, thread flag and error-log call order','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['OS queue and thread-flag providers remain open','Final agent-content callback, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
