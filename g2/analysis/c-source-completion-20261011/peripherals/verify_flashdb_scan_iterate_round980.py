#!/usr/bin/env python3
"""Native/C FlashDB seven-argument sector scan loop."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-scan-iterate-round980';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_scan_iterate.c'
obj=out/'settings_flashdb_scan_iterate.o'
base=root/'build/c-firmware/flashdb-space-search-round979/apollo-main-flashdb-space-search.o'
linked=out/'apollo-main-flashdb-scan-iterate.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544736-0x438000:0x5447b6-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
struct sector_info;
uint32_t g2_flashdb_read_sector_info(uint32_t a,uint32_t b,struct sector_info*c,_Bool d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_flashdb_next_sector_addr(uint32_t a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_scan_iterate',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for steps in (1,2):
  for mode in (0,1,2):
   for sector_type in (1,2):
    for refresh in (0,1):
     for callback in (False,True):
      for callback_result in (0,1):
       outputs=[]
       for compiled in (False,True):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x100000)
        for addr,data in segs:uc.mem_write(addr,data)
        uc.mem_map(0x20000000,0x200000)
        db=0x20010000;sector=0x20010100;arg1=0x20010200;arg2=0x20010300
        uc.mem_write(db,b'\0'*0x100);uc.mem_write(db+12,(0x100).to_bytes(4,'little'));uc.mem_write(db+20,(0x2000).to_bytes(4,'little'))
        uc.mem_write(sector,b'\0'*32)
        hooks={((syms['g2_flashdb_read_sector_info'] if compiled else 0x54418e)&~1):'read',
               ((syms['g2_flashdb_next_sector_addr'] if compiled else 0x544374)&~1):'next',
                0x100800:'callback'}
        calls=[];reads=0;nexts=0
        def hook(cpu,address,size,user):
         kind=hooks.get(address)
         if not kind:return
         r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
         if kind=='read':
          calls.append(('read',r[0]-db,r[1],r[2]-sector,r[3]));cpu.mem_write(sector+1,bytes([sector_type]));ret=0
         elif kind=='next':
          calls.append(('next',r[0]-db,r[1]-sector,r[2]));ret=0x2100 if len([x for x in calls if x[0]=='next'])<steps else 0xffffffff
         else:calls.append(('callback',r[0]-sector,r[1]-arg1,r[2]-arg2));ret=callback_result
         cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook)
        sp=0x201ff000
        uc.mem_write(sp,arg2.to_bytes(4,'little')+((0x100801 if callback else 0)).to_bytes(4,'little')+refresh.to_bytes(4,'little'))
        for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,sector),(A.UC_ARM_REG_R2,mode),(A.UC_ARM_REG_R3,arg1),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
        uc.emu_start((syms['audio_flashdb_scan_iterate'] if compiled else 0x544736)|1,0x600000,count=180)
        outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0)))
       assert outputs[0]==outputs[1],(steps,mode,sector_type,refresh,callback,callback_result,outputs)
       cases.append((steps,mode,sector_type,refresh,callback,callback_result))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_scan_iterate'}
assert after-before==set()
receipt={'round':980,'status':'PASS_NATIVE_FLASHDB_SCAN_ITERATE','component':'Apollo seven-argument FlashDB sector scanner 0x544736',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C read/filter/refresh/callback/next calls and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Exact sector-read and next-sector providers are selected C bodies; their lower flash/cache semantics remain gated','Other FlashDB write providers and DB row placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
