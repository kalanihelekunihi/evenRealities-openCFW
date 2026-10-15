#!/usr/bin/env python3
"""Native/C Apollo FlashDB GC copy callback with controlled providers."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-gc-copy-round983';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_gc_copy.c'
obj=out/'settings_flashdb_gc_copy.o'
base=root/'build/c-firmware/flashdb-sector-advance-round982/apollo-main-flashdb-sector-advance.o'
linked=out/'apollo-main-flashdb-gc-copy.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544b98-0x438000:0x544c78-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
struct sector_info;
uint32_t g2_flashdb_write_status(uint32_t a,uint32_t b,uint8_t*c,uint32_t d,uint32_t e,uint32_t f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t g2_flashdb_read_kv(uint32_t a,void*b){(void)a;(void)b;return 0;}
uint32_t audio_flashdb_gc_move(uint32_t a,void*b){(void)a;(void)b;return 0;}
uint32_t g2_flashdb_next_kv_addr(uint32_t a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_flashdb_gc_erase(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_next_sector_addr(uint32_t a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_read_sector_info(uint32_t a,uint32_t b,struct sector_info*c,_Bool d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_flashdb_db_path(uint32_t a){(void)a;return 0;}
int32_t g2_flashdb_print(const char*a,...){(void)a;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_gc_copy_callback',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'status':'g2_flashdb_write_status','read_kv':'g2_flashdb_read_kv','move':'audio_flashdb_gc_move','next_kv':'g2_flashdb_next_kv_addr','erase':'audio_flashdb_gc_erase','next_sector':'g2_flashdb_next_sector_addr','read_sector':'g2_flashdb_read_sector_info','path':'g2_flashdb_db_path','print':'g2_flashdb_print'}
 addrs={'status':0x5858d8,'read_kv':0x544000,'move':0x5449c0,'next_kv':0x543f8c,'erase':0x5445f2,'next_sector':0x544374,'read_sector':0x54418e,'path':0x585c94,'print':0x4733ee}
 cases=[]
 for active in (False,True):
  for kvvalid in (False,True):
   for move_result in (0,1):
    for read_result in (0,1):
     for remain in (0x80,0x200):
      outputs=[]
      for compiled in (False,True):
       uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
       uc.mem_map(0x100000,0x100000)
       for addr,data in segs:uc.mem_write(addr,data)
       uc.mem_map(0x20000000,0x200000)
       db=0x20010000;sector=0x20011000;ctx=0x20012000;name=0x20013000;path=0x20013100
       uc.mem_write(db,b'\0'*0x100);uc.mem_write(db,name.to_bytes(4,'little'))
       uc.mem_write(sector,b'\0'*24);uc.mem_write(sector,bytes([1 if active else 0,0,2]));uc.mem_write(sector+4,(0x3000).to_bytes(4,'little'))
       uc.mem_write(ctx,db.to_bytes(4,'little')+(0x100).to_bytes(4,'little')+(0x4000).to_bytes(4,'little'))
       uc.mem_write(name,b'dbname\0');uc.mem_write(path,b'/db/path\0')
       hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in addrs.items()}
       calls=[];kvptr=[]
       def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
       def hook(cpu,address,size,user):
        kind=hooks.get(address)
        if not kind:return
        r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
        sp=cpu.reg_read(A.UC_ARM_REG_SP)
        if kind=='status':
         extra=[int.from_bytes(cpu.mem_read(sp+i*4,4),'little') for i in range(2)]
         calls.append(('status',r[0]-db,r[1],r[3],*extra));ret=0
        elif kind=='read_kv':
         kvptr.append(r[1]);calls.append(('read_kv',r[0]-db,int.from_bytes(cpu.mem_read(r[1]+80,4),'little')))
         cpu.mem_write(r[1],bytes([2,1 if kvvalid else 0,4])+b'\0'*13+b'name');ret=0
        elif kind=='move':calls.append(('move',r[0]-db,r[1]-kvptr[-1]));ret=move_result
        elif kind=='next_kv':calls.append(('next_kv',r[0]-db,r[1]-sector,r[2]-kvptr[-1]));ret=0xffffffff
        elif kind=='erase':calls.append(('erase',r[0]-db,r[1],r[2]));ret=0
        elif kind=='next_sector':calls.append(('next_sector',r[0]-db,r[1]-sector,r[2]));ret=0x5000
        elif kind=='read_sector':
         calls.append(('read_sector',r[0]-db,r[1],r[3]));cpu.mem_write(r[2]+16,remain.to_bytes(4,'little'));ret=read_result
        elif kind=='path':calls.append(('path',r[0]-db));ret=path
        else:
         fmt=string(r[0]);args=(string(r[1]),string(r[2])) if fmt=='[%s][%s] ' else ((r[1],string(r[2])) if fmt.startswith('Error: Moved') else ())
         calls.append(('print',fmt,args));ret=0
        cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
       uc.hook_add(UC_HOOK_CODE,hook)
       for reg,val in ((A.UC_ARM_REG_R0,sector),(A.UC_ARM_REG_R1,ctx),(A.UC_ARM_REG_R2,0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
       uc.emu_start((syms['audio_flashdb_gc_copy_callback'] if compiled else 0x544b98)|1,0x600000,count=300)
       outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(ctx,12)),bytes(uc.mem_read(db+20,4))))
      assert outputs[0]==outputs[1],(active,kvvalid,move_result,read_result,remain,outputs)
      cases.append((active,kvvalid,move_result,read_result,remain))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_gc_copy_callback'}
assert after-before=={'audio_flashdb_gc_move','audio_flashdb_gc_erase'}
receipt={'round':983,'status':'PASS_NATIVE_FLASHDB_GC_COPY','component':'Apollo FlashDB GC copy callback 0x544b98',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C active gate, write/read/move/next/erase and sector state under controlled children',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['GC move 0x5449c0 and erase 0x5445f2 remain open','DB row placement and other FlashDB write providers remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
