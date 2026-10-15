#!/usr/bin/env python3
"""Native/C terminal-data per-record flag clear at Apollo 0x597664."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-record-flags-round923';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_record_flags_clear_all.c'
obj=out/'td_record_flags_clear_all.o'
base=root/'build/c-firmware/td-state-cluster-round922/apollo-main-td-state-cluster.o'
linked=out/'apollo-main-td-record-flags.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597664-0x438000:0x59769c-0x438000]
assert int.from_bytes(blob[0x597c08-0x438000:0x597c0c-0x438000],'little')==0x2010fd20
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 state=root/'components/audio/uart_thread_source_candidate/td_state.c'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_record_flags_clear_all',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for count in (0,1,2,9,10,11,255,0xffffffff):
  for pattern in (0xff,0x5a):
   outputs=[]
   for compiled in (False,True):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
    uc.mem_map(0x100000,0x100000)
    for addr,data in segs:uc.mem_write(addr,data)
    uc.mem_map(0x20000000,0x200000)
    addr=syms['audio_td_state'] if compiled else 0x2010fd20
    uc.mem_write(addr,bytes([pattern])*0xa1dc)
    uc.mem_write(addr+0x9568,count.to_bytes(4,'little'))
    uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
    uc.emu_start(((syms['audio_td_record_flags_clear_all'] if compiled else 0x597664)|1),0x600000,count=3000)
    outputs.append(bytes(uc.mem_read(addr+0x9550,0x700)))
   assert outputs[0]==outputs[1],(count,pattern)
   cases.append((count,pattern))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_record_flags_clear_all'}
assert after-before==set()
receipt={'round':923,'status':'PASS_NATIVE_TD_RECORD_FLAGS_CLEAR','component':'Apollo terminal-data record flags clear 0x597664','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'native_ram':'0x2010fd20+0x9568,0x95f4,0x9684+0x90*i','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Remaining new-session children include ring reset and flag-set with reset','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
