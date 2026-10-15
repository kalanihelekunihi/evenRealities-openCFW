#!/usr/bin/env python3
"""Native/C Apollo terminal-data bounded ASR ring writer."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-ring-write-round936';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_ring_write.c';state=sd/'td_state.c'
obj=out/'td_ring_write.o'
base=root/'build/c-firmware/td-state-pointers-round935/apollo-main-td-state-pointers.o'
linked=out/'apollo-main-td-ring-write.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5976d8-0x438000:0x5977ce-0x438000]
assert hashlib.sha256(native).hexdigest()=='2325e26f174de422c6cf6268410502e37a241ef4c5449eaf3f54daf2256d4487'
assert int.from_bytes(blob[0x597c08-0x438000:0x597c0c-0x438000],'little')==0x2010fd20
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_ring_write',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for length in (0,1,5,256,512):
  for published,cached in ((0,0),(5,2),(2,5),(2047,2047),(2050,2050)):
   for sentence_final in (0,1):
    for all_final in (0,1):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
      uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      addr=syms['audio_td_state'] if compiled else 0x2010fd20
      uc.mem_write(addr,bytes([0x5a])*0xa1dc)
      uc.mem_write(addr+0x800,published.to_bytes(2,'little'))
      uc.mem_write(addr+0x802,cached.to_bytes(2,'little'))
      packet=bytearray(0x204);packet[0:2]=length.to_bytes(2,'little')
      packet[2:514]=bytes(i&255 for i in range(512))
      packet[0x202]=sentence_final;packet[0x203]=all_final
      uc.mem_write(0x20076000,bytes(packet))
      calls=[]
      if not compiled:
       def hook(cpu,address,size,user):
        if address!=0x439be4:return
        dst=cpu.reg_read(A.UC_ARM_REG_R0);srcptr=cpu.reg_read(A.UC_ARM_REG_R1);n=cpu.reg_read(A.UC_ARM_REG_R2)
        calls.append((dst,srcptr,n));cpu.mem_write(dst,bytes(cpu.mem_read(srcptr,n)))
        cpu.reg_write(A.UC_ARM_REG_R0,dst);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
       uc.hook_add(UC_HOOK_CODE,hook)
      uc.reg_write(A.UC_ARM_REG_R0,0x20076000);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
      uc.emu_start(((syms['audio_td_ring_write'] if compiled else 0x5976d8)|1),0x600000,count=10000)
      outputs.append((bytes(uc.mem_read(addr,0x806)),uc.reg_read(A.UC_ARM_REG_R0)))
     assert outputs[0]==outputs[1],(length,published,cached,sentence_final,all_final,[(i,a,b) for i,(a,b) in enumerate(zip(outputs[0][0],outputs[1][0])) if a!=b][:12],outputs[0][1],outputs[1][1])
     cases.append((length,published,cached,sentence_final,all_final))
 for compiled in (False,True):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  uc.reg_write(A.UC_ARM_REG_R0,0);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
  uc.emu_start(((syms['audio_td_ring_write'] if compiled else 0x5976d8)|1),0x600000,count=100)
  assert uc.reg_read(A.UC_ARM_REG_R0)==0xffffffff
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_ring_write'}
assert after-before==set()
receipt={'round':936,'status':'PASS_NATIVE_TD_RING_WRITE','component':'Apollo td_ring_write 0x5976d8','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases)+1,'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'terminal_handlers_compiled':6,'terminal_handlers_total':12,'whole_image_complete':False,'hardware_proof':False,'gates':['6 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open','Final linker placement and boot initialization of terminal-data cluster remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases)+1,len(before),len(after))
