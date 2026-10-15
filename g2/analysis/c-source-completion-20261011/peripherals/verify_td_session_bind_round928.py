#!/usr/bin/env python3
"""Native/C terminal-data session bind store and active-session check."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-session-bind-round928';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_session_bind.c';state=sd/'td_state.c'
obj=out/'td_session_bind.o'
base=root/'build/c-firmware/terminal-request-display-round927/apollo-main-terminal-request-display.o'
linked=out/'apollo-main-td-session-bind.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x597c08-0x438000:0x597c0c-0x438000],'little')==0x2010fd20
native_bind=blob[0x5979b2-0x438000:0x5979ce-0x438000]
native_active=blob[0x5973b2-0x438000:0x5973d4-0x438000]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_session_bind_store',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for current in (0,1,0x12345678):
  for active in (0,1,2):
   for session in (0,1,0xffffffff):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
     uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     addr=syms['audio_td_state'] if compiled else 0x2010fd20
     uc.mem_write(addr,bytes([0x5a])*0xa1dc)
     uc.mem_write(addr+0x9560,current.to_bytes(4,'little'))
     uc.mem_write(addr+0xa1d9,bytes([active]))
     def call(name,entry,arg=None):
      uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
      if arg is not None:uc.reg_write(A.UC_ARM_REG_R0,arg)
      uc.emu_start(((syms[name] if compiled else entry)|1),0x600000,count=1000)
      return uc.reg_read(A.UC_ARM_REG_R0)
     before=call('audio_td_has_active_session',0x5973b2)
     call('audio_td_session_bind_store',0x5979b2,session)
     after=call('audio_td_has_active_session',0x5973b2)
     outputs.append((before,after,bytes(uc.mem_read(addr+0x955c,16)),bytes(uc.mem_read(addr+0xa1d8,4))))
    assert outputs[0]==outputs[1],(current,active,session,outputs)
    cases.append((current,active,session))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':928,'status':'PASS_NATIVE_TD_SESSION_BIND','component':'Apollo td_session_bind_store 0x5979b2 and td_has_active_session 0x5973b2','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_bind_sha256':hashlib.sha256(native_bind).hexdigest(),'native_active_sha256':hashlib.sha256(native_active).hexdigest(),'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['terminal_apply_session_id_changed 0x5e8346 remains open, including its other children','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
