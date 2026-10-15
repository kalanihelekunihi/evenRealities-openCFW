#!/usr/bin/env python3
"""Native/C terminal session status-name lookup across all byte inputs."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-status-name-round930';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_session_status_name.c'
obj=out/'terminal_session_status_name.o'
base=root/'build/c-firmware/terminal-cached-status-round929/apollo-main-terminal-cached-status.o'
linked=out/'apollo-main-terminal-status-name.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e82a4-0x438000:0x5e82e6-0x438000]
assert hashlib.sha256(native).hexdigest()=='ccb4fd214848e313cec9bccf37b644d5eb49e51974346e2f93c459ab35589cb1'
labels=[b'SESSION_STATUS_NONE',b'SESSION_STATUS_THINKING',b'SESSION_STATUS_AWAIT_USER',b'SESSION_STATUS_DONE',b'SESSION_STATUS_RESET',b'SESSION_STATUS_SYNC_END',b'SESSION_STATUS_UNKNOWN']
for literal,label in zip((0x5e8c24,0x5e8c28,0x5e8c2c,0x5e8c30,0x5e8c34,0x5e8c38,0x5e8e3c),labels):
 ptr=int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')
 assert blob[ptr-0x438000:].split(b'\0')[0]==label
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_session_status_name',str(src),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for value in list(range(256))+[0x100,0x101,0x105,0xffffffff]:
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x100000)
   uc.reg_write(A.UC_ARM_REG_R0,value);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms['audio_terminal_session_status_name'] if compiled else 0x5e82a4)|1),0x600000,count=100)
   ptr=uc.reg_read(A.UC_ARM_REG_R0)
   outputs.append(bytes(uc.mem_read(ptr,64)).split(b'\0')[0])
  assert outputs[0]==outputs[1],(value,outputs)
  cases.append(value)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':930,'status':'PASS_NATIVE_TERMINAL_STATUS_NAME','component':'Apollo semantic_terminal_session_status_name 0x5e82a4','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'all_status_bytes':True,'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Parent terminal_apply_session_id_changed 0x5e8346 remains open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
