#!/usr/bin/env python3
"""Native/C full terminal-data reset and source-owned display queue cell."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-state-reset-round926';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_state_reset.c';queue=sd/'terminal_display_queue_handle.c'
objects=[]
for source in (src,queue):
 obj=out/(source.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
 objects.append(obj)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def word(addr):return int.from_bytes(blob[addr-0x438000:addr-0x438000+4],'little')
assert word(0x597c08)==0x2010fd20 and word(0x597be0)==0x20110d74
assert word(0x597c04)==0x20074a88 and word(0x5e4784)==0x20074a90
native=blob[0x5970f0-0x438000:0x597108-0x438000]
assert hashlib.sha256(native).hexdigest()=='907d99adf6ef1c8d507c141c22fcc5670b63ac90895c290bd3601fad75662772'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_state_reset',str(src),str(sd/'td_session_ring_reset.c'),str(sd/'td_state.c'),str(queue),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for counter,pattern in [(0,0xff),(0xffffffff,0x5a)]:
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
   counter_addr=syms['audio_td_ring_reset_counter'] if compiled else 0x20074a88
   queue_addr=syms['audio_terminal_display_queue_handle'] if compiled else 0x20074a90
   uc.mem_write(state_addr,bytes([pattern])*0xa1dc)
   uc.mem_write(counter_addr,counter.to_bytes(4,'little'))
   uc.mem_write(queue_addr,(0x12345678).to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(cpu,address,size,user):
     if address!=0x43c0e4:return
     p=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1);v=cpu.reg_read(A.UC_ARM_REG_R2)
     calls.append((p,n,v));cpu.mem_write(p,bytes([v&255])*n)
     cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE,hook)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms['audio_td_state_reset'] if compiled else 0x5970f0)|1),0x600000,count=700000)
   outputs.append((bytes(uc.mem_read(state_addr,0xa1dc)),bytes(uc.mem_read(counter_addr,4)),bytes(uc.mem_read(queue_addr,4))))
   if not compiled:assert calls==[(0x2010fd20,0xa1dc,0),(0x20110d74,0x850c,0)],calls
  assert outputs[0]==outputs[1],(counter,pattern)
  assert outputs[0][2]==(0x12345678).to_bytes(4,'little')
  cases.append((counter,pattern))
base=root/'build/c-firmware/td-flag-reset-round925/apollo-main-td-flag-reset.o'
linked=out/'apollo-main-td-state-reset.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(o) for o in objects],'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':926,'status':'PASS_NATIVE_TD_STATE_RESET_AND_QUEUE_CELL','component':'Apollo terminal-data full reset 0x5970f0 and display queue RAM cell','sources':[{'path':str(s.relative_to(root)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in (src,queue)],'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'bytes_cleared':0xa1dc,'native_queue_cell':'0x20074a90','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Runtime queue handle initialization and final RAM linker placement remain unverified','terminal_request_display return contract remains open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
