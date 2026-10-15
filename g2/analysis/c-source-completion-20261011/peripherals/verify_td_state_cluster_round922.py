#!/usr/bin/env python3
"""Consolidate overlapping Apollo terminal-data RAM state and relink providers."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-state-cluster-round922';out.mkdir(parents=True,exist_ok=True)
source_dir=root/'components/audio/uart_thread_source_candidate'
names=['td_state.c','td_notify_state_clear.c','td_session_struct_clear.c']
sources=[source_dir/n for n in names]
objects=[]
for src in sources:
 obj=out/(src.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
 objects.append(obj)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def word(a):return int.from_bytes(blob[a-0x438000:a-0x438000+4],'little')
assert word(0x597c08)==0x2010fd20 and word(0x597c0c)==0x20110528
assert word(0x597c0c)-word(0x597c08)==0x808
assert word(0x597be0)==0x20110d74 and word(0x597be0)-word(0x597c08)==0x1054
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_notify_state_clear',*[str(x) for x in sources],'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for native_entry,compiled_name,offset,length in [(0x597110,'audio_td_notify_state_clear',0,0x806),(0x597124,'audio_td_session_struct_clear',0x808,0x84c)]:
  for pattern in (0,0xff,0x5a):
   results=[]
   for compiled in (False,True):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
    uc.mem_map(0x100000,0x100000)
    for addr,data in segs:uc.mem_write(addr,data)
    uc.mem_map(0x20000000,0x200000)
    base=syms['audio_td_state'] if compiled else 0x2010fd20
    uc.mem_write(base,bytes([pattern])*0xa1dc)
    calls=[]
    if not compiled:
     def hook(cpu,address,size,user):
      if address!=0x43c0e4:return
      p=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1);v=cpu.reg_read(A.UC_ARM_REG_R2)
      calls.append((p,n,v));cpu.mem_write(p,bytes([v&255])*n)
      cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
    uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
    uc.emu_start(((syms[compiled_name] if compiled else native_entry)|1),0x600000,count=22000)
    results.append(bytes(uc.mem_read(base,0x1054)))
    if not compiled:assert calls==[(base+offset,length,0)],calls
   assert results[0]==results[1],(native_entry,pattern)
   expect=bytes([pattern])*offset+bytes(length)+bytes([pattern])*(0x1054-offset-length)
   assert results[0]==expect
   cases.append((native_entry,pattern))
base=root/'build/c-firmware/terminal-handler-round916/apollo-main-terminal-handler.o'
old=root/'build/c-firmware/terminal-output-reset-round921/apollo-main-terminal-output-reset.o'
prior=[root/'build/c-firmware/terminal-handler-round918/terminal_command_5e9f74.o',root/'build/c-firmware/terminal-handler-round919/terminal_command_5e9ec8.o',root/'build/c-firmware/terminal-output-reset-round921/terminal_reset_output_tracking.o']
linked=out/'apollo-main-td-state-cluster.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(x) for x in prior],*[str(x) for x in objects],'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(linked)==imports(old)-{'audio_td_state'}
assert len(imports(linked))==620
receipt={'round':922,'status':'PASS_NATIVE_TD_STATE_CLUSTER','component':'Apollo terminal-data RAM cluster 0x2010fd20..0x20119efb','sources':[{'path':str(s.relative_to(root)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in sources],'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cluster_bytes':0xa1dc,'clear_cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'supersedes_receipts':[917,920,921],'whole_image_complete':False,'hardware_proof':False,'gates':['Final linker RAM placement and boot initialization of 0xa1dc-byte terminal-data cluster remain unverified','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
