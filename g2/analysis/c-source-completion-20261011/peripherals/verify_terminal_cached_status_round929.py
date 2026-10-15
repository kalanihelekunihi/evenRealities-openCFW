#!/usr/bin/env python3
"""Native/C active-session pointer and cached-status scan."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-cached-status-round929';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'terminal_cached_session_status.c';state=sd/'td_state.c'
obj=out/'terminal_cached_session_status.o'
base=root/'build/c-firmware/td-session-bind-round928/apollo-main-td-session-bind.o'
linked=out/'apollo-main-terminal-cached-status.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x597c08-0x438000:0x597c0c-0x438000],'little')==0x2010fd20
native_active=blob[0x59732a-0x438000:0x597344-0x438000]
native_status=blob[0x5e830c-0x438000:0x5e8346-0x438000]
assert hashlib.sha256(native_active).hexdigest()=='f2b1aade4da6570646835dd3fa051ba82663994b48c760691debeaf541c4ca5e'
assert hashlib.sha256(native_status).hexdigest()=='b0a4909e6c5a3510fd6a373c99f786d84c9b6834dcd9f259814ba03b15b6593a'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_cached_session_status',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for active in (0,1,2):
  for count in (0,1,3,10):
   for query in (0,0x1000,0x1001,0x1009,0x7777):
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
     for i in range(10):
      uc.mem_write(addr+0x9560+0x9c+i*0x90,(0x1000+i).to_bytes(4,'little'))
      uc.mem_write(addr+0x9560+0x122+i*0x90,bytes([0x20+i]))
     uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
     uc.emu_start(((syms['audio_td_active_session'] if compiled else 0x59732a)|1),0x600000,count=100)
     ptr=uc.reg_read(A.UC_ARM_REG_R0)
     assert ptr==(addr+0x9560 if active else 0),(compiled,active,hex(ptr))
     uc.reg_write(A.UC_ARM_REG_R0,query);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
     uc.emu_start(((syms['audio_terminal_cached_session_status'] if compiled else 0x5e830c)|1),0x600000,count=1000)
     outputs.append(uc.reg_read(A.UC_ARM_REG_R0))
    assert outputs[0]==outputs[1],(active,count,query,outputs)
    cases.append((active,count,query))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':929,'status':'PASS_NATIVE_TERMINAL_CACHED_STATUS','component':'Apollo td_active_session 0x59732a and cached status 0x5e830c','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_active_sha256':hashlib.sha256(native_active).hexdigest(),'native_status_sha256':hashlib.sha256(native_status).hexdigest(),'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Parent terminal_apply_session_id_changed 0x5e8346 remains open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
