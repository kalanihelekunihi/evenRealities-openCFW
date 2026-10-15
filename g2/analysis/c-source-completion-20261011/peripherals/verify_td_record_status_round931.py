#!/usr/bin/env python3
"""Native/C Apollo terminal-data record status writes."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-record-status-round931';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_record_status_set.c';state=sd/'td_state.c'
obj=out/'td_record_status_set.o'
base=root/'build/c-firmware/terminal-status-name-round930/apollo-main-terminal-status-name.o'
linked=out/'apollo-main-td-record-status.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597464-0x438000:0x5974d4-0x438000]
assert hashlib.sha256(native).hexdigest()=='d3a7bfe74a3b6f520f5019eac100de4e76ea9bfcf4f199145f90fcaf7dd9fc69'
assert int.from_bytes(blob[0x597c1c-0x438000:0x597c20-0x438000],'little')==0x20119312
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_record_status_set',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for active in (0,1):
  for count in (0,1,3,10,11):
   for session in (0xffffffff,0,0x1000,0x1001,0x1009,0x7777):
    for status in (0,2,255):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
      uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      addr=syms['audio_td_state'] if compiled else 0x2010fd20
      uc.mem_write(addr,bytes([0x5a])*0xa1dc)
      uc.mem_write(addr+0xa1d9,bytes([active]))
      uc.mem_write(addr+0x9568,count.to_bytes(4,'little'))
      for i in range(10):uc.mem_write(addr+0x95fc+i*0x90,(0x1000+i).to_bytes(4,'little'))
      uc.reg_write(A.UC_ARM_REG_R0,session);uc.reg_write(A.UC_ARM_REG_R1,status)
      uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
      uc.emu_start(((syms['audio_td_record_status_set'] if compiled else 0x597464)|1),0x600000,count=1000)
      outputs.append(bytes(uc.mem_read(addr+0x9550,0x680)))
     assert outputs[0]==outputs[1],(active,count,session,status)
     cases.append((active,count,session,status))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':931,'status':'PASS_NATIVE_TD_RECORD_STATUS','component':'Apollo td_record_status_set 0x597464','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Parent terminal_apply_session_id_changed 0x5e8346 and helper 0x5ecafa remain open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
