#!/usr/bin/env python3
"""Native/C current-session index helper chain."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-current-index-round932';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_current_session_index.c'
obj=out/'td_current_session_index.o'
base=root/'build/c-firmware/td-record-status-round931/apollo-main-td-record-status.o'
linked=out/'apollo-main-td-current-index.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={n:hashlib.sha256(blob[a-0x438000:b-0x438000]).hexdigest() for n,a,b in [('count',0x5eca48,0x5eca64),('signed',0x5ecaac,0x5ecafa),('unsigned',0x5ecafa,0x5ecb08)]}
assert native=={'count':'697cef08c4e9cd3e19252dd694d77521e1f2e2df88bbd985c5e92a4f1d416186','signed':'967a1fe1194426b782b75db8ff154616e68a5849138705e37e755119742142f8','unsigned':'2259b6cb84bccc85afcd3706f2f67ac21d93976c806a55bda369b456c9a6a367'}
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_current_session_index',str(src),str(sd/'td_session_bind.c'),str(sd/'terminal_cached_session_status.c'),str(sd/'td_state.c'),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for active in (0,1):
  for current in (0,0x1000,0x1002,0x1009,0x7777):
   for count in (0,1,3,10,11):
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
     uc.mem_write(addr+0x9564,current.to_bytes(4,'little'))
     uc.mem_write(addr+0x9568,count.to_bytes(4,'little'))
     uc.mem_write(addr+0x9560,(1).to_bytes(4,'little'))
     for i in range(10):uc.mem_write(addr+0x95fc+i*0x90,(0x1000+i).to_bytes(4,'little'))
     result=[]
     for name,entry in [('audio_td_active_record_count',0x5eca48),('audio_td_current_session_index_signed',0x5ecaac),('audio_td_current_session_index',0x5ecafa)]:
      uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
      uc.emu_start(((syms[name] if compiled else entry)|1),0x600000,count=1000)
      result.append(uc.reg_read(A.UC_ARM_REG_R0))
     outputs.append(result)
    assert outputs[0]==outputs[1],(active,current,count,outputs)
    cases.append((active,current,count))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':932,'status':'PASS_NATIVE_TD_CURRENT_SESSION_INDEX','component':'Apollo terminal-data current-session index 0x5eca48/5ecaac/5ecafa','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':native,'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Parent terminal_apply_session_id_changed 0x5e8346 remains open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
