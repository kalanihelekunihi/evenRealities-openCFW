#!/usr/bin/env python3
"""Native/C Apollo runtime candidate selection at child-call boundaries."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-candidate-session-round946';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_candidate_session_for_runtime.c'
obj=out/'terminal_candidate_session_for_runtime.o'
base=root/'build/c-firmware/td-record-status-lookup-round945/apollo-main-td-record-status-lookup.o'
linked=out/'apollo-main-terminal-candidate-session.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e505a-0x438000:0x5e50ea-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_terminal_runtime_saved_session;
uint8_t *audio_td_active_records_ptr(void){return (uint8_t*)0;}
uint32_t audio_td_counter_b_get(void){return 0;}
uint8_t audio_td_record_status_for_session(uint32_t x){(void)x;return 0;}
uint8_t audio_td_session_marked(uint32_t x){(void)x;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_candidate_session_for_runtime',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'records':'audio_td_active_records_ptr','current':'audio_td_counter_b_get','status':'audio_td_record_status_for_session','marked':'audio_td_session_marked'}
 native_addrs={'records':0x59732a,'current':0x5973dc,'status':0x5973e4,'marked':0x597544}
 def run(compiled,active,saved,current,saved_status,current_status,saved_mark,current_mark,count,row_status,row_mark):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  records=0x2010fd20+0x9560
  uc.mem_write(records+8,count.to_bytes(4,'little'))
  for i in range(3):
   uc.mem_write(records+i*0x90+0x122,bytes([row_status if i==1 else 1]))
   uc.mem_write(records+i*0x90+0x9c,(0x3000+i).to_bytes(4,'little'))
  saved_addr=syms['audio_terminal_runtime_saved_session'] if compiled else 0x2006e358
  uc.mem_write(saved_addr,saved.to_bytes(4,'little'))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   value=cpu.reg_read(A.UC_ARM_REG_R0)
   calls.append((name,value if name in ('status','marked') else None))
   if name=='records':result=records if active else 0
   elif name=='current':result=current
   elif name=='status':result=saved_status if value==saved else current_status if value==current else 0
   else:result=saved_mark if value==saved else current_mark if value==current else row_mark
   cpu.reg_write(A.UC_ARM_REG_R0,result)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0xdeadbeef),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_candidate_session_for_runtime'] if compiled else 0x5e505a)|1),0x600000,count=1000)
  return uc.reg_read(A.UC_ARM_REG_R0),tuple(calls)
 cases=[]
 for active in (False,True):
  for saved in (0,0x1000):
   for current in (0,0x2000):
    for saved_status in (1,2):
     for current_status in (1,2):
      for saved_mark in (0,1):
       for current_mark in (0,1):
        for count,row_status,row_mark in ((0,2,0),(1,2,0),(2,1,0),(2,2,0),(3,2,1)):
         args=(active,saved,current,saved_status,current_status,saved_mark,current_mark,count,row_status,row_mark)
         n=run(False,*args);c=run(True,*args)
         assert n==c,(args,n,c)
         cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_candidate_session_for_runtime'}
assert after-before=={'audio_td_active_records_ptr','audio_td_session_marked'}
receipt={'round':946,'status':'PASS_NATIVE_TERMINAL_CANDIDATE_SESSION','component':'Apollo terminal candidate-session selector 0x5e505a','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C saved-current-record selection, child call order and selected session','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Active-record pointer 0x59732a and marked-session predicate 0x597544 remain open','Final RAM placement/initialization and callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
