#!/usr/bin/env python3
"""Native/C session ring reset and wrapper memory differential."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-ring-reset-round924';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_session_ring_reset.c'
state=root/'components/audio/uart_thread_source_candidate/td_state.c'
obj=out/'td_session_ring_reset.o'
base=root/'build/c-firmware/td-record-flags-round923/apollo-main-td-record-flags.o'
linked=out/'apollo-main-td-ring-reset.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x597be0-0x438000:0x597be4-0x438000],'little')==0x20110d74
assert int.from_bytes(blob[0x597c04-0x438000:0x597c08-0x438000],'little')==0x20074a88
ring_native=blob[0x5970c0-0x438000:0x5970f0-0x438000]
wrapper_native=blob[0x597108-0x438000:0x597110-0x438000]
assert hashlib.sha256(ring_native).hexdigest()=='0ef6681f6a95ee33d7ca630c83f5fde30ca4a3b5dff16ceb664c35cd27f054b5'
assert hashlib.sha256(wrapper_native).hexdigest()=='17b39126b50a4eddab9f8545c4a277e6e9a5fde38b6e39e3571d569d333f6fca'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_ring_reset_wrapper',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for counter,pattern in [(0,0xff),(1,0x5a),(0xffffffff,0xa5)]:
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
   counter_addr=syms['audio_td_ring_reset_counter'] if compiled else 0x20074a88
   uc.mem_write(state_addr,bytes([pattern])*0xa1dc)
   uc.mem_write(counter_addr,counter.to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(cpu,address,size,user):
     if address!=0x43c0e4:return
     p=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1);v=cpu.reg_read(A.UC_ARM_REG_R2)
     calls.append((p,n,v));cpu.mem_write(p,bytes([v&255])*n)
     cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE,hook)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms['audio_td_ring_reset_wrapper'] if compiled else 0x597108)|1),0x600000,count=500000)
   outputs.append((bytes(uc.mem_read(state_addr,0xa1dc)),bytes(uc.mem_read(counter_addr,4))))
   if not compiled:assert calls==[(0x20110d74,0x850c,0)],calls
  assert outputs[0]==outputs[1],(counter,pattern)
  expected_count=(counter+1)&0xffffffff
  assert int.from_bytes(outputs[0][1],'little')==expected_count
  assert outputs[0][0][0x1054:0x9558]==bytes(0x8504)
  assert int.from_bytes(outputs[0][0][0x9558:0x955c],'little')==expected_count
  assert int.from_bytes(outputs[0][0][0x955c:0x9560],'little')==1
  cases.append((counter,pattern))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_ring_reset_wrapper'}
assert after-before==set()
receipt={'round':924,'status':'PASS_NATIVE_TD_RING_RESET','component':'Apollo terminal-data session ring reset 0x5970c0 and wrapper 0x597108','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_ring_body_sha256':hashlib.sha256(ring_native).hexdigest(),'native_wrapper_body_sha256':hashlib.sha256(wrapper_native).hexdigest(),'cases':len(cases),'bytes_cleared':0x850c,'native_cluster_base':'0x2010fd20','native_counter':'0x20074a88','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Final linker placement and boot initialization of ring counter and terminal-data cluster remain unverified','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
