#!/usr/bin/env python3
"""Native/C FlashDB valid-alignment GC sector erase contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-gc-erase-round984';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_gc_erase.c'
obj=out/'settings_flashdb_gc_erase.o'
base=root/'build/c-firmware/flashdb-gc-copy-round983/apollo-main-flashdb-gc-copy.o'
linked=out/'apollo-main-flashdb-gc-erase.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5445f2-0x438000:0x5446b8-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_flashdb_partition_erase(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_set_status(uint8_t*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_flash_write(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void g2_flashdb_update_sector_cache(uint32_t a,const void*b){(void)a;(void)b;}
uint32_t g2_flashdb_db_path(uint32_t a){(void)a;return 0;}
int32_t g2_flashdb_print(const char*a,...){(void)a;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_gc_erase',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'erase':'audio_flashdb_partition_erase','status':'g2_flashdb_set_status','write':'g2_flashdb_flash_write','cache':'g2_flashdb_update_sector_cache'}
 addrs={'erase':0x585a32,'status':0x585870,'write':0x585a52,'cache':0x543c48}
 cases=[]
 for address in (0,0x3000):
  for marker in (0,0xffffffff):
   for erase_result in (0,1,0x100):
    for write_result in (0,2,0x102):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      db=0x20010000;uc.mem_write(db,b'\0'*0x100);uc.mem_write(db+12,(0x1000).to_bytes(4,'little'))
      hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in addrs.items()}
      calls=[];header_ptr=[]
      def hook(cpu,pc,size,user):
       kind=hooks.get(pc)
       if not kind:return
       r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
       sp=cpu.reg_read(A.UC_ARM_REG_SP)
       if kind=='erase':calls.append(('erase',r[0]-db,r[1],r[2]));ret=erase_result
       elif kind=='status':
        if not header_ptr:header_ptr.append(r[0])
        calls.append(('status',r[0]-header_ptr[0],r[1],r[2]));ret=0
       elif kind=='write':
        extra=int.from_bytes(cpu.mem_read(sp,4),'little')
        calls.append(('write',r[0]-db,r[1],r[3],extra,bytes(cpu.mem_read(r[2],16))));ret=write_result
       else:calls.append(('cache',r[0]-db,bytes(cpu.mem_read(r[1],24))));ret=0
       cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
      uc.hook_add(UC_HOOK_CODE,hook)
      for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,address),(A.UC_ARM_REG_R2,marker),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
      uc.emu_start((syms['audio_flashdb_gc_erase'] if compiled else 0x5445f2)|1,0x600000,count=220)
      outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0)))
     assert outputs[0]==outputs[1],(address,marker,erase_result,write_result,outputs)
     cases.append((address,marker,erase_result,write_result))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_gc_erase'}
assert after-before=={'audio_flashdb_partition_erase'}
receipt={'round':984,'status':'PASS_NATIVE_FLASHDB_GC_ERASE_ALIGNED','component':'Apollo FlashDB GC erase 0x5445f2 aligned path',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C aligned erase, status bytes, 16-byte header write, cache sector and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Misaligned nonreturning assertion not emulated','Partition erase 0x585a32 remains open','DB row placement and other FlashDB write providers remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
