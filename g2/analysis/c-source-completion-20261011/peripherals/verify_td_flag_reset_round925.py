#!/usr/bin/env python3
"""Native/C terminal-data flag reset and temporary record memory differential."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-flag-reset-round925';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_flag_set_with_reset.c'
state=root/'components/audio/uart_thread_source_candidate/td_state.c'
obj=out/'td_flag_set_with_reset.o'
base=root/'build/c-firmware/td-ring-reset-round924/apollo-main-td-ring-reset.o'
linked=out/'apollo-main-td-flag-reset.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x597c08-0x438000:0x597c0c-0x438000],'little')==0x2010fd20
assert int.from_bytes(blob[0x597c34-0x438000:0x597c38-0x438000],'little')==0x20119efa
native={name:hashlib.sha256(blob[start-0x438000:end-0x438000]).hexdigest() for name,start,end in [('clear',0x5971cc,0x5971f6),('invalidate',0x5971f6,0x59722c),('set',0x597572,0x59758e)]}
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_flag_set_with_reset',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for enabled,flag,pattern in [(e,f,p) for e in (0,1,255) for f in (0,7,0xffffffff) for p in (0xff,0x5a)]:
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   addr=syms['audio_td_state'] if compiled else 0x2010fd20
   uc.mem_write(addr,bytes([pattern])*0xa1dc)
   uc.mem_write(addr+0x9564,flag.to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(cpu,address,size,user):
     if address!=0x43c0e4:return
     p=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1);v=cpu.reg_read(A.UC_ARM_REG_R2)
     calls.append((p,n,v));cpu.mem_write(p,bytes([v&255])*n)
     cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE,hook)
   uc.reg_write(A.UC_ARM_REG_R0,enabled);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms['audio_td_flag_set_with_reset'] if compiled else 0x597572)|1),0x600000,count=3000)
   outputs.append(bytes(uc.mem_read(addr,0xa1dc)))
   if not compiled:assert calls==[(0x2010fd20+0x956c,0x90,0)],calls
  assert outputs[0]==outputs[1],(enabled,flag,pattern)
  cases.append((enabled,flag,pattern))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_flag_set_with_reset'}
assert after-before==set()
receipt={'round':925,'status':'PASS_NATIVE_TD_FLAG_RESET','component':'Apollo terminal-data flag and temporary-record reset 0x5971cc/1f6/572','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':native,'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Final linker placement and boot initialization of terminal-data cluster remain unverified','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
