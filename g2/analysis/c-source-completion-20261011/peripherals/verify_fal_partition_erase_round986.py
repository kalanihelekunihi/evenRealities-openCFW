#!/usr/bin/env python3
"""Native/C FAL partition erase bounds, device selection and callback."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/fal-partition-erase-round986';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_fal_partition_erase.c'
obj=out/'settings_fal_partition_erase.o'
base=root/'build/c-firmware/flashdb-partition-erase-round985/apollo-main-flashdb-partition-erase.o'
linked=out/'apollo-main-fal-partition-erase.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597db0-0x438000:0x597dea-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t g2_fal_device_for_partition(uint32_t a){(void)a;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_fal_partition_erase',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for address,size in ((0,0),(0x100,0x100),(0x1000,0x1000),(0xffffffff,2)):
  for device_present in (False,True):
   for callback_result in (0,1,0xffffffff):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     part=0x20010000;device=0x20011000
     uc.mem_write(part,b'\0'*0x100);uc.mem_write(part+0x34,(0x3000).to_bytes(4,'little'));uc.mem_write(part+0x38,(0x1000).to_bytes(4,'little'))
     uc.mem_write(device+0x30,(0x100801).to_bytes(4,'little'))
     selector=(syms['g2_fal_device_for_partition'] if compiled else 0x597d10)&~1
     calls=[]
     def hook(cpu,pc,insn,user):
      if pc==selector:
       calls.append(('select',cpu.reg_read(A.UC_ARM_REG_R0)-part));ret=device if device_present else 0
      elif pc==0x100800:
       calls.append(('erase',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)));ret=callback_result
      else:return
      cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     for reg,val in ((A.UC_ARM_REG_R0,part),(A.UC_ARM_REG_R1,address),(A.UC_ARM_REG_R2,size),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start((syms['audio_fal_partition_erase'] if compiled else 0x597db0)|1,0x600000,count=100)
     outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0)))
    assert outputs[0]==outputs[1],(address,size,device_present,callback_result,outputs)
    cases.append((address,size,device_present,callback_result))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_fal_partition_erase'} and after-before==set()
receipt={'round':986,'status':'PASS_NATIVE_FAL_PARTITION_ERASE','component':'Apollo FAL partition erase 0x597db0',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C overflow-aware bound, selected device, erase callback args and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Device selection and physical FAL erase remain lower contracts','GC move and DB row placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
