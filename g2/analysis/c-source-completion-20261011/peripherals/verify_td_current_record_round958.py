#!/usr/bin/env python3
"""Native/C Apollo current-record pointer and sentinel lookup."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-current-record-round958';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_current_record.c';state=sd/'td_state.c'
obj=out/'td_current_record.o'
base=root/'build/c-firmware/td-bind-temp-timer-round957/apollo-main-td-bind-temp-timer.o'
linked=out/'apollo-main-td-current-record.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597188-0x438000:0x5971cc-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_td_find_record_index(uint32_t x,uint32_t *p){(void)x;(void)p;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_current_record',str(src),str(state),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for session in (0,1,0x1234,0xffffffff):
  for sentinel in (0,0xffffffff):
   for found in (0,1):
    for index in (0,1,9):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
      uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
      uc.mem_write(state_addr+0x956c,sentinel.to_bytes(4,'little'))
      child=(syms['audio_td_find_record_index'] if compiled else 0x597138)&~1
      calls=[]
      def hook(cpu,address,size,user):
       if address!=child:return
       r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
       calls.append(r0)
       cpu.mem_write(r1,index.to_bytes(4,'little'))
       cpu.reg_write(A.UC_ARM_REG_R0,found)
       cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
      uc.hook_add(UC_HOOK_CODE,hook)
      for reg,val in ((A.UC_ARM_REG_R0,session),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
      uc.emu_start(((syms['audio_td_current_record'] if compiled else 0x597188)|1),0x600000,count=200)
      ptr=uc.reg_read(A.UC_ARM_REG_R0)
      outputs.append((0 if ptr==0 else ptr-state_addr,tuple(calls)))
     assert outputs[0]==outputs[1],(session,sentinel,found,index,outputs)
     cases.append((session,sentinel,found,index))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_current_record'} and not after-before
receipt={'round':958,'status':'PASS_NATIVE_TD_CURRENT_RECORD','component':'Apollo current-record pointer 0x597188','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C sentinel path, child lookup call and relative pointer result','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Session-list item logger 0x5e9b84 remains open','3 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
