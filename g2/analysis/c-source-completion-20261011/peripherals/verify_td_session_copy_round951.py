#!/usr/bin/env python3
"""Native/C Apollo session structure copy-out contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-session-copy-round951';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_session_struct_copy_out.c';state=sd/'td_state.c'
obj=out/'td_session_struct_copy_out.o'
base=root/'build/c-firmware/terminal-query-round950/apollo-main-terminal-query.o'
linked=out/'apollo-main-td-session-copy.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597be4-0x438000:0x597c02-0x438000]
assert int.from_bytes(blob[0x597c0c-0x438000:0x597c10-0x438000],'little')==0x20110528
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t native_copy(uint8_t *d,const uint8_t *s,uint32_t n){(void)d;(void)s;(void)n;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_session_struct_copy_out',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for present in (False,True):
  for seed in (0,1,73,255):
   outputs=[]
   for compiled in (False,True):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
    uc.mem_map(0x100000,0x100000)
    for addr,data in segs:uc.mem_write(addr,data)
    uc.mem_map(0x20000000,0x200000)
    source=0x20010000;dest=(syms['audio_td_state']+0x808) if compiled else 0x20110528
    data=bytes((seed+i*37)&255 for i in range(0x84c))
    uc.mem_write(source,data);uc.mem_write(dest,b'\xa5'*0x84c)
    calls=[]
    if not compiled:
     def hook(cpu,address,size,user):
      if address!=0x439be4:return
      d=cpu.reg_read(A.UC_ARM_REG_R0);s=cpu.reg_read(A.UC_ARM_REG_R1);n=cpu.reg_read(A.UC_ARM_REG_R2)
      calls.append((d==dest,s==source,n))
      cpu.mem_write(d,bytes(cpu.mem_read(s,n)))
      cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
    for reg,val in ((A.UC_ARM_REG_R0,source if present else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
    uc.emu_start(((syms['audio_td_session_struct_copy_out'] if compiled else 0x597be4)|1),0x600000,count=10000)
    if compiled:calls=([(True,True,0x84c)] if present else [])
    outputs.append((uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(dest,0x84c)),tuple(calls)))
   assert outputs[0]==outputs[1],(present,seed,outputs[0][0],outputs[1][0])
   cases.append((present,seed))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_session_struct_copy_out'} and not after-before
receipt={'round':951,'status':'PASS_NATIVE_TD_SESSION_COPY','component':'Apollo session structure copy-out 0x597be4','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native child copy arguments and C full 0x84c-byte destination image','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Session-match helper 0x5e818a remains open','4 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
