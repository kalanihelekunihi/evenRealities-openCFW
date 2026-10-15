#!/usr/bin/env python3
"""Native/C terminal-data pointer getter offsets."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-state-pointers-round935';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_state_pointers.c';state=sd/'td_state.c'
obj=out/'td_state_pointers.o'
base=root/'build/c-firmware/terminal-asr-round934/apollo-main-terminal-asr.o'
linked=out/'apollo-main-td-state-pointers.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entries=[('audio_td_state_ptr',0x597318,0x597c08,0),('audio_td_session_struct_ptr',0x59731e,0x597c0c,0x808),('audio_td_ring_ptr',0x597324,0x597be0,0x1054)]
for name,entry,literal,offset in entries:
 assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')==0x2010fd20+offset
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_state_ptr',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,entry,literal,offset in entries:
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms[name] if compiled else entry)|1),0x600000,count=30)
   expected=(syms['audio_td_state'] if compiled else 0x2010fd20)+offset
   assert uc.reg_read(A.UC_ARM_REG_R0)==expected,(name,compiled)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_state_ptr'}
assert after-before==set()
receipt={'round':935,'status':'PASS_NATIVE_TD_STATE_POINTERS','component':'Apollo terminal-data pointer getters 0x597318/31e/324','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_bodies_sha256':{name:hashlib.sha256(blob[entry-0x438000:entry+6-0x438000]).hexdigest() for name,entry,_,_ in entries},'cases':len(entries),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['td_ring_write 0x5976d8 remains open','6 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(entries),len(before),len(after))
