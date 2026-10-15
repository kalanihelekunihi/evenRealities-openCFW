#!/usr/bin/env python3
"""Native/C FlashDB GC count callback state mutation."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-gc-count-round981';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_gc_count.c'
obj=out/'settings_flashdb_gc_count.o'
base=root/'build/c-firmware/flashdb-scan-iterate-round980/apollo-main-flashdb-scan-iterate.o'
linked=out/'apollo-main-flashdb-gc-count.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544b84-0x438000:0x544b98-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_gc_count_callback',str(src),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for present in (0,1,255):
  for initial in (0,1,0xffffffff):
   for address in (0,0x12345678,0xffffffff):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     rec=0x20010000;count=0x20010100;out_addr=0x20010200
     uc.mem_write(rec,bytes([present])+b'\0'*3+address.to_bytes(4,'little'))
     uc.mem_write(count,initial.to_bytes(4,'little'));uc.mem_write(out_addr,(0xaaaaaaaa).to_bytes(4,'little'))
     for reg,val in ((A.UC_ARM_REG_R0,rec),(A.UC_ARM_REG_R1,count),(A.UC_ARM_REG_R2,out_addr),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start((syms['audio_flashdb_gc_count_callback'] if compiled else 0x544b84)|1,0x600000,count=60)
     outputs.append((uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(count,4)),bytes(uc.mem_read(out_addr,4))))
    assert outputs[0]==outputs[1],(present,initial,address,outputs)
    cases.append((present,initial,address))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before==after
receipt={'round':981,'status':'PASS_NATIVE_FLASHDB_GC_COUNT','component':'Apollo FlashDB GC sector count callback 0x544b84',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C presence gate, count wrap, address copy and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['GC copy callback 0x544b98 and sector-advance parent 0x544c78 remain open','DB row placement and other FlashDB write providers remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
