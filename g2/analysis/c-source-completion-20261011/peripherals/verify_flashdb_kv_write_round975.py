#!/usr/bin/env python3
"""Native/C FlashDB KV write core with controlled lower providers."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-kv-write-round975';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_kv_write.c'
obj=out/'settings_flashdb_kv_write.o'
base=root/'build/c-firmware/flashdb-blob-store-round974/apollo-main-flashdb-blob-store.o'
linked=out/'apollo-main-flashdb-kv-write.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x544f6c-0x438000:0x54503a-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t g2_log_candidate_module_length(const uint8_t*a){(void)a;return 0;}
uint32_t g2_flashdb_find_kv(uint32_t a,uint32_t b,void*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_flashdb_prepare_sector(void*a,void*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_flashdb_kv_delete(void*a,const char*b,void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_flashdb_store_value(void*a,void*b,const char*c,const void*d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void audio_flashdb_sector_advance(void*a,uint32_t b){(void)a;(void)b;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_kv_write',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'strlen':'g2_log_candidate_module_length','find':'g2_flashdb_find_kv','prepare':'audio_flashdb_prepare_sector','delete':'audio_flashdb_kv_delete','write':'audio_flashdb_store_value','advance':'audio_flashdb_sector_advance'}
 native_addrs={'strlen':0x44a43c,'find':0x54449a,'prepare':0x544b78,'delete':0x5448b4,'write':0x544d60,'advance':0x544c78}
 cases=[]
 for present in (False,True):
  for prepare in (0,0xffffffff):
   for found in (0,1):
    for deleted in (0,1):
     for written in (0,1):
      for flag in (0,1):
       outputs=[]
       for compiled in (False,True):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x100000)
        for addr,data in segs:uc.mem_write(addr,data)
        uc.mem_map(0x20000000,0x200000)
        db=0x20010000;key=0x20011000;data=0x20012000
        uc.mem_write(db,b'\0'*0x100);uc.mem_write(db+0x30,bytes([flag]));uc.mem_write(key,b'kvTerminalMode\0');uc.mem_write(data,bytes(range(16)))
        hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in native_addrs.items()}
        calls=[];delete_count=0
        def hook(cpu,address,size,user):
         kind=hooks.get(address)
         if not kind:return
         r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
         sp=cpu.reg_read(A.UC_ARM_REG_SP)
         used={'strlen':1,'prepare':4,'find':3,'delete':4,'write':4,'advance':2}[kind]
         args=tuple(r[:used])
         if kind=='write':args+= (int.from_bytes(cpu.mem_read(sp,4),'little'),)
         calls.append((kind,args))
         if kind=='strlen':ret=14
         elif kind=='prepare':ret=prepare
         elif kind=='find':ret=found
         elif kind=='delete':ret=deleted
         elif kind=='write':ret=written
         else:ret=0
         cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook)
        for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,key),(A.UC_ARM_REG_R2,data if present else 0),(A.UC_ARM_REG_R3,0x1234),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
        uc.emu_start((syms['audio_flashdb_kv_write'] if compiled else 0x544f6c)|1,0x600000,count=250)
        outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0)))
       assert outputs[0]==outputs[1],(present,prepare,found,deleted,written,flag,outputs)
       cases.append((present,prepare,found,deleted,written,flag))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_kv_write'}
assert after-before=={'audio_flashdb_prepare_sector','audio_flashdb_kv_delete','audio_flashdb_store_value','audio_flashdb_sector_advance'}
receipt={'round':975,'status':'PASS_NATIVE_FLASHDB_KV_WRITE_CORE','component':'Apollo FlashDB KV write core 0x544f6c',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C delete/write branches, prepare/find/status child order, sector advance and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Four lower FlashDB write providers remain open','DB rows initialization/linker placement remains open','Final terminal callback and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
