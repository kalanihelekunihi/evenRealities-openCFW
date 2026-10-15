#!/usr/bin/env python3
"""Native/C Apollo record index search including output-pointer behavior."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-find-record-index-round949';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_find_record_index.c';state=sd/'td_state.c'
obj=out/'td_find_record_index.o'
base=root/'build/c-firmware/td-session-marked-round948/apollo-main-td-session-marked.o'
linked=out/'apollo-main-td-find-record-index.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597138-0x438000:0x597188-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_find_record_index',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for active in (0,1,255):
  for count in (0,1,3,10,11,0xffffffff):
   for session in (0,0x1000,0x1001,0x1009,0x100a,0x7777):
    for pointer in (False,True):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
      uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
      uc.mem_write(state_addr,bytes([0x5a])*0xa1dc)
      uc.mem_write(state_addr+0xa1d9,bytes([active]))
      uc.mem_write(state_addr+0x9568,count.to_bytes(4,'little'))
      for i in range(10):uc.mem_write(state_addr+0x95fc+i*0x90,(0x1000+i).to_bytes(4,'little'))
      slot=0x201ff100;uc.mem_write(slot,(0xdeadbeef).to_bytes(4,'little'))
      for reg,val in ((A.UC_ARM_REG_R0,session),(A.UC_ARM_REG_R1,slot if pointer else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
      uc.emu_start(((syms['audio_td_find_record_index'] if compiled else 0x597138)|1),0x600000,count=1000)
      outputs.append((uc.reg_read(A.UC_ARM_REG_R0),int.from_bytes(uc.mem_read(slot,4),'little')))
     assert outputs[0]==outputs[1],(active,count,session,pointer,outputs)
     cases.append((active,count,session,pointer))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_find_record_index'} and not after-before
receipt={'round':949,'status':'PASS_NATIVE_TD_FIND_RECORD_INDEX','component':'Apollo record-index lookup 0x597138','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C active flag, count clamp, row match and output pointer','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Final RAM placement/initialization and terminal callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
