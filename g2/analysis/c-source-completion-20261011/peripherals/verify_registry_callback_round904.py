#!/usr/bin/env python3
"""Verify the 0x5bf24a no-op registry callback and selected Apollo link."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-callback-round904';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_callback_5bf24a.c'
obj=out/'registry_callback_5bf24a.o'
base=root/'build/c-firmware/fault-handler-round903/apollo-main-fault-handler.o'
linked=out/'apollo-main-registry-callback.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5bf24a-0x438000:0x5bf24e-0x438000]
assert native==bytes.fromhex('00207047')
row=struct.unpack_from('<4I',blob,0x6a4550-0x438000)
assert row[0]==0x109 and (row[1]&~1)==0x5bf24a
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_5bf24a',
                 str(src),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for event,payload,length in [(0,0,0),(2,0x20076000,4),(5,0xffffffff,0xffffffff),(0x109,0x12345678,0x87654321)]:
  results=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x100000)
   for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,payload),
                   (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_SP,0x200ff000),
                   (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
   uc.emu_start(((syms['audio_uart_registry_callback_5bf24a'] if compiled else 0x5bf24a)|1),
                0x600000,count=100)
   results.append((uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_SP)))
  assert results[0]==results[1]==(0,0x200ff000)
  cases.append([event,payload,length])
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_uart_registry_callback_5bf24a'} and not after-before
receipt={'round':904,'status':'PASS_NATIVE_REGISTRY_CALLBACK_5BF24A',
 'component':'Apollo UI registry callback 0x5bf24a',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'registry_row':hex(0x6a4550),'cases':cases,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'registry_callback_bodies_complete':14,'registry_callback_bodies_total':64,
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['50 registry callback bodies, unknown fault-code behavior, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
