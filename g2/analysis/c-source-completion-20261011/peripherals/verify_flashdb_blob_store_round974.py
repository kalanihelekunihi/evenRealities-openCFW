#!/usr/bin/env python3
"""Native/C Apollo FlashDB blob-store gateway branch and callback contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-blob-store-round974';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_blob_store.c'
obj=out/'settings_flashdb_blob_store.o'
base=root/'build/c-firmware/flashdb-blob-write-round973/apollo-main-flashdb-blob-write.o'
linked=out/'apollo-main-flashdb-blob-store.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x54503a-0x438000:0x54509e-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t g2_flashdb_db_path(uint32_t a){(void)a;return 0;}
int32_t g2_flashdb_print(const char*a,...){(void)a;return 0;}
uint32_t audio_flashdb_kv_write(void*a,const char*b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_blob_store',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for initialized in (0,1):
  for lock in (0,1):
   for unlock in (0,1):
    for result in (0,1,0x1234,0xffffffff):
     outputs=[]
     for compiled in (False,True):
      uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
      uc.mem_map(0x100000,0x100000)
      for addr,data in segs:uc.mem_write(addr,data)
      uc.mem_map(0x20000000,0x200000)
      db=0x20010000;key=0x20010100;data=0x20010200;desc=0x20010300;name=0x20010400;path=0x20010500
      uc.mem_write(db,b'\0'*64);uc.mem_write(db,name.to_bytes(4,'little'))
      uc.mem_write(db+24,bytes([initialized]));uc.mem_write(db+28,((0x100801 if lock else 0)).to_bytes(4,'little'))
      uc.mem_write(db+32,((0x100901 if unlock else 0)).to_bytes(4,'little'))
      uc.mem_write(key,b'kvTerminalMode\0');uc.mem_write(data,bytes(range(16)))
      uc.mem_write(desc,data.to_bytes(4,'little')+(0x12345).to_bytes(4,'little'))
      uc.mem_write(name,b'dbname\0');uc.mem_write(path,b'/db/path\0')
      hooks={((syms['g2_flashdb_db_path'] if compiled else 0x585c94)&~1):'path',
             ((syms['g2_flashdb_print'] if compiled else 0x4733ee)&~1):'print',
             ((syms['audio_flashdb_kv_write'] if compiled else 0x544f6c)&~1):'write',
             0x100800:'lock',0x100900:'unlock'}
      calls=[]
      def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
      def hook(cpu,address,size,user):
       kind=hooks.get(address)
       if not kind:return
       r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
       if kind=='path':calls.append(('path',r[0]-db));ret=path
       elif kind=='print':
        fmt=string(r[0]);calls.append(('print',fmt,string(r[1]) if fmt=='[%s][%s] ' else '',string(r[2]) if fmt=='[%s][%s] ' else (string(r[1]) if fmt.startswith('Error:') else '')));ret=0
       elif kind=='write':calls.append(('write',r[0]-db,r[1]-key,r[2]-data,r[3]));ret=result
       else:calls.append((kind,r[0]-db));ret=0
       cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
      uc.hook_add(UC_HOOK_CODE,hook)
      for reg,val in ((A.UC_ARM_REG_R0,db),(A.UC_ARM_REG_R1,key),(A.UC_ARM_REG_R2,desc),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
      uc.emu_start((syms['audio_flashdb_blob_store'] if compiled else 0x54503a)|1,0x600000,count=150)
      outputs.append((calls,uc.reg_read(A.UC_ARM_REG_R0)))
     assert outputs[0]==outputs[1],(initialized,lock,unlock,result,outputs)
     cases.append((initialized,lock,unlock,result))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_flashdb_blob_store'}
assert after-before=={'audio_flashdb_kv_write'}
receipt={'round':974,'status':'PASS_NATIVE_FLASHDB_BLOB_STORE','component':'Apollo FlashDB blob-store gateway 0x54503a',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C initialization gate, print calls, optional lock/unlock, KV write args, uint8 return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['KV write core 0x544f6c remains open','DB rows initialization/linker placement remains open','Final terminal callback and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
