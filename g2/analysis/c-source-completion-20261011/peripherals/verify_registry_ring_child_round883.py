#!/usr/bin/env python3
"""Verify the ring-task forwarding child and selected Apollo linkage."""
from pathlib import Path
import hashlib,json,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-ring-child-round883';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_child_4c548c.c'
obj=out/'registry_child_4c548c.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
imports={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()}
assert imports=={'audio_uart_ring_task_msg_send'}
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
addr=0x4c548c;child=0x4c549c
native=blob[addr-0x438000:addr+16-0x438000]
assert native.hex()=='80b50a0092b20100022000f001f802bd'
assert hashlib.sha256(native).hexdigest()=='ca041a24cffbcb08b27531154b822d996c893d63e557a9dfeca0a85836b9f12b'
observations=[]
for payload,length in ((0,0),(0x12345678,0x87654321),(0xffffffff,0xffffffff)):
 uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 uc.mem_map(0x4c5000,0x1000)
 uc.mem_write(addr,native);uc.mem_write(child,b'\x70\x47')
 uc.mem_map(0x20000000,0x1000)
 for reg,value in ((A.UC_ARM_REG_R0,payload),(A.UC_ARM_REG_R1,length),
                   (A.UC_ARM_REG_SP,0x20000800),(A.UC_ARM_REG_LR,0x4c54b1)):
  uc.reg_write(reg,value)
 calls=[]
 def hook(cpu,address,size,user):
  if address==child:calls.append([cpu.reg_read(A.UC_ARM_REG_R0),
                                  cpu.reg_read(A.UC_ARM_REG_R1),
                                  cpu.reg_read(A.UC_ARM_REG_R2)])
 uc.hook_add(UC_HOOK_CODE,hook)
 uc.emu_start(addr|1,0x4c54b0,count=20)
 assert calls==[[2,payload,length&0xffff]]
 observations.append({'input':[payload,length],'child_args':calls[0]})
base=root/'build/c-firmware/ui-registry-table-round882/apollo-main-ui-registry-source.o'
linked=out/'apollo-main-registry-ring-child.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_registry_child_4c548c'} and not after-before
assert 'audio_uart_ring_task_msg_send' not in after
receipt={'round':883,'status':'PASS_NATIVE_REGISTRY_RING_FORWARD_CHILD',
         'component':'Apollo registry-to-ring forwarding',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'observations':observations,'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Other registry forwarding children, callback bodies, and RAM contexts remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_REGISTRY_RING_CHILD',len(after))
