#!/usr/bin/env python3
"""Native/C FlashDB allocation search and one GC retry."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-prepare-space-round977';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_prepare_space.c'
obj=out/'settings_flashdb_prepare_space.o'
base=root/'build/c-firmware/flashdb-prepare-sector-round976/apollo-main-flashdb-prepare-sector.o'
linked=out/'apollo-main-flashdb-prepare-space.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544af2-0x438000:0x544b6a-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
int32_t audio_flashdb_space_search(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void audio_flashdb_sector_advance(void*a,uint32_t b){(void)a;(void)b;}
uint32_t g2_flashdb_db_path(uint32_t a){(void)a;return 0;}
int32_t g2_flashdb_print(const char*a,...){(void)a;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_prepare_space',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'search':'audio_flashdb_space_search','advance':'audio_flashdb_sector_advance','path':'g2_flashdb_db_path','print':'g2_flashdb_print'}
 native_addrs={'search':0x544814,'advance':0x544c78,'path':0x585c94,'print':0x4733ee}
 cases=[]
 for flag in (0,1):
  for first in (0,7,0xffffffff):
   for second in (0,9,0xffffffff):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     db=0x20010000;sector=db+0x8c;path=0x20010500;name=0x20010400
     uc.mem_write(db,b'\0'*0x100);uc.mem_write(db,name.to_bytes(4,'little'));uc.mem_write(db+0x30,bytes([flag]))
     uc.mem_write(path,b'/db/path\0');uc.mem_write(name,b'dbname\0')
     hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in native_addrs.items()}
     calls=[];searches=[]
     def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
     def hook(cpu,address,size,user):
      kind=hooks.get(address)
      if not kind:return
      r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(3)]
      if kind=='search':calls.append(('search',r[0]-db,r[1]-sector,r[2]));ret=first if not searches else second;searches.append(ret)
      elif kind=='advance':calls.append(('advance',r[0]-db,r[1]));ret=0
      elif kind=='path':calls.append(('path',r[0]-db));ret=path
      else:
       fmt=string(r[0]);args=(string(r[1]),string(r[2])) if fmt=='[%s][%s] ' else ((r[1],) if fmt.startswith('Error: Alloc') else ())
       calls.append(('print',fmt,args));ret=0
      cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,sector),(A.UC_ARM_REG_R2,0x12345),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start((syms['audio_flashdb_prepare_space'] if compiled else 0x544af2)|1,0x600000,count=150)
     outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(db+0x30,1))))
    assert outputs[0]==outputs[1],(flag,first,second,outputs)
    cases.append((flag,first,second))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_prepare_space'}
assert after-before=={'audio_flashdb_space_search'}
receipt={'round':977,'status':'PASS_NATIVE_FLASHDB_PREPARE_SPACE','component':'Apollo FlashDB allocation and GC retry 0x544af2',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C first search, optional one GC retry, diagnostics, flag clear and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['FlashDB space search 0x544814 remains open','Sector advance and other write providers remain open','DB rows initialization/linker placement remains open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
