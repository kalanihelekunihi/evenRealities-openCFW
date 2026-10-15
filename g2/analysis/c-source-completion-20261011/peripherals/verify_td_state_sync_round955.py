#!/usr/bin/env python3
"""Native/C Apollo td_state_sync complete RAM transition."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-state-sync-round955';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_state_sync.c';state=sd/'td_state.c'
obj=out/'td_state_sync.o'
base=root/'build/c-firmware/td-flag-b-round954/apollo-main-td-flag-b.o'
linked=out/'apollo-main-td-state-sync.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5977ce-0x438000:0x5978ee-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_state_sync',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,present,old_count,new_count,match,status):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
  source=0x20010000
  initial=bytearray((i*11+0x3a)&255 for i in range(0xa1dc))
  initial[0x9568:0x956c]=old_count.to_bytes(4,'little')
  initial[0xa1d9]=0x2a
  for i in range(10):
   row=0x95fc+i*0x90
   initial[row:row+4]=(0x1000+i).to_bytes(4,'little')
   initial[row+0x88:row+0x8c]=(0x5000+i).to_bytes(4,'little')
   initial[row+0x8c]=0x60+i
  uc.mem_write(state_addr,bytes(initial))
  p=bytearray((i*17+0x21)&255 for i in range(0x900))
  p[:4]=(0xaaaa).to_bytes(4,'little');p[4:8]=(0xbbbb).to_bytes(4,'little');p[8:10]=new_count.to_bytes(2,'little')
  for i in range(10):
   row=0xc+i*0x88
   p[row:row+4]=((0x1000+((i+1)%10)) if match else (0x3000+i)).to_bytes(4,'little')
   p[row+0x86]=status
  uc.mem_write(source,bytes(p))
  calls=[]
  if not compiled:
   def hook(cpu,address,size,user):
    if address!=0x439be4:return
    d=cpu.reg_read(A.UC_ARM_REG_R0);s=cpu.reg_read(A.UC_ARM_REG_R1);n=cpu.reg_read(A.UC_ARM_REG_R2)
    calls.append((d-state_addr,s-source if s>=source and s<source+len(p) else s-state_addr,n))
    cpu.mem_write(d,bytes(cpu.mem_read(s,n)))
    cpu.reg_write(A.UC_ARM_REG_R0,d)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,source if present else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_td_state_sync'] if compiled else 0x5977ce)|1),0x600000,count=20000)
  result=uc.reg_read(A.UC_ARM_REG_R0)
  memory=bytes(uc.mem_read(state_addr+0x9560,0xa1dc-0x9560))
  return result,memory,tuple(calls)
 cases=[]
 for present in (False,True):
  for old_count in (0,1,3,10,11):
   for new_count in (0,1,3,10,11):
    for match in (False,True):
     for status in (0,1,2,3):
      args=(present,old_count,new_count,match,status)
      n=run(False,*args);c=run(True,*args)
      assert n[:2]==c[:2],(args,n[0],c[0],next((i for i,(a,b) in enumerate(zip(n[1],c[1])) if a!=b),None),n[2])
      cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_state_sync'} and not after-before
receipt={'round':955,'status':'PASS_NATIVE_TD_STATE_SYNC','component':'Apollo td_state_sync 0x5977ce','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C entire active and backup RAM ranges, header, count clamp, record copy and matching field carryover','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Three exposed session-list child routines remain open','3 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
