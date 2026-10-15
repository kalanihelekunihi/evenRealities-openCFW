#!/usr/bin/env python3
"""Native/C FlashDB sector-advance scanner routing."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-sector-advance-round982';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_sector_advance.c'
count_src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_gc_count.c'
obj=out/'settings_flashdb_sector_advance.o'
base=root/'build/c-firmware/flashdb-gc-count-round981/apollo-main-flashdb-gc-count.o'
linked=out/'apollo-main-flashdb-sector-advance.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544c78-0x438000:0x544cd4-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_flashdb_gc_copy_callback(void*a,void*b,void*c){(void)a;(void)b;(void)c;return 0;}
void *audio_flashdb_scan_iterate(void*a,void*b,uint32_t c,void*d,void*e,uint32_t (*f)(void*,void*,void*),uint32_t g){(void)a;(void)b;(void)c;(void)e;(void)f;(void)g;return d;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_sector_advance',str(src),str(count_src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for count in (0,1,2,0xffffffff):
  for address in (0,0x12345678):
   for size in (0,0x100,0xffffffff):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     db=0x20010000;uc.mem_write(db,b'\0'*0x100);uc.mem_write(db+0x30,b'\x01')
     child=(syms['audio_flashdb_scan_iterate'] if compiled else 0x544736)&~1
     count_cb=(syms['audio_flashdb_gc_count_callback']|1) if compiled else 0x544b85
     copy_cb=(syms['audio_flashdb_gc_copy_callback']|1) if compiled else 0x544b99
     calls=[];sector_ptr=[]
     def hook(cpu,pc,insn,user):
      if pc!=child:return
      r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
      sp=cpu.reg_read(A.UC_ARM_REG_SP)
      arg2=int.from_bytes(cpu.mem_read(sp,4),'little')
      callback=int.from_bytes(cpu.mem_read(sp+4,4),'little')
      refresh=int.from_bytes(cpu.mem_read(sp+8,4),'little')
      assert r[0]==db and refresh==0
      sector_ptr.append(r[1])
      if r[2]==1:
       assert callback==count_cb and arg2!=0
       calls.append(('count',int.from_bytes(cpu.mem_read(r[3],4),'little'),int.from_bytes(cpu.mem_read(arg2,4),'little')))
       cpu.mem_write(r[3],count.to_bytes(4,'little'));cpu.mem_write(arg2,address.to_bytes(4,'little'))
      else:
       assert r[2]==0 and callback==copy_cb and arg2==0
       ctx=[int.from_bytes(cpu.mem_read(r[3]+i*4,4),'little') for i in range(3)]
       calls.append(('copy',ctx[0]-db,ctx[1],ctx[2]))
      cpu.reg_write(A.UC_ARM_REG_R0,r[3]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,size),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start((syms['audio_flashdb_sector_advance'] if compiled else 0x544c78)|1,0x600000,count=130)
     assert len(set(sector_ptr))==1
     outputs.append((calls,bytes(uc.mem_read(db+0x30,1))))
    assert outputs[0]==outputs[1],(count,address,size,outputs)
    cases.append((count,address,size))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_sector_advance'}
assert after-before=={'audio_flashdb_gc_copy_callback'}
receipt={'round':982,'status':'PASS_NATIVE_FLASHDB_SECTOR_ADVANCE','component':'Apollo FlashDB sector-advance router 0x544c78',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C first count scan, conditional copy scan, callback identities, flag clear',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['GC copy callback 0x544b98 remains open','Other FlashDB write providers and DB row placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
