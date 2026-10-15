#!/usr/bin/env python3
"""AUDM registry callback and message-type8 child against native ARM traces."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-audm-round888';out.mkdir(parents=True,exist_ok=True)
srcs=[root/'components/audio/uart_thread_source_candidate'/name for name in
      ('registry_callback_54f912.c','aud_message_type8_53cd40.c')]
objs=[]
for src in srcs:
 obj=out/(src.stem+'.o');objs.append(obj)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                 '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                 '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native_cb=blob[0x54f912-0x438000:0x54f976-0x438000]
native_child=blob[0x53cd40-0x438000:0x53cd62-0x438000]
assert native_cb[:2].hex()=='38b5' and native_cb[-2:].hex()=='30bd'
assert native_child[:2].hex()=='1fb5' and native_child[-2:].hex()=='1fbd'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
void audio_aud_message_dispatch_53c638(const void *a){(void)a;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_54f912',
                 *(str(x) for x in srcs),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,valid,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(0x20076000,b'\x9a')
  native_addrs={'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e,'dispatch':0x53c638}
  names={'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output','dispatch':'audio_aud_message_dispatch_53c638'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,140)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='dispatch':calls.append(('dispatch',tuple(int.from_bytes(cpu.mem_read(r0+4*i,4),'little') for i in range(3))))
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(4)]
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),vals[2],vals[3]))
   elif op=='compact':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    last=int.from_bytes(cpu.mem_read(sp,4),'little')
    calls.append(('compact',r0,string(r1),string(r2),r3,last))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  payload=0x20076000 if valid in ('yes','zero_length') else 0
  length=0 if valid=='zero_length' else 0x12345
  for reg,val in ((A.UC_ARM_REG_R0,0x11223344),(A.UC_ARM_REG_R1,payload),
                  (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_uart_registry_callback_54f912'] if compiled else 0x54f912)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for valid,flags in (('yes',0),('yes',7),('null',0),('null',7),('zero_length',2),('zero_length',4)):
  n=run(False,valid,flags);c=run(True,valid,flags)
  assert n==c,(valid,flags,n,c)
  cases.append({'input':valid,'flags':flags,'calls':len(n[0]),'return':n[1]})

base=root/'build/c-firmware/registry-settings-callback-round887/apollo-main-registry-settings-callback.o'
linked=out/'apollo-main-registry-audm.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),*(str(o) for o in objs),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_registry_callback_54f912'}
assert after-before=={'audio_aud_message_dispatch_53c638'}
receipt={'round':888,'status':'PASS_NATIVE_REGISTRY_AUDM_CALLBACK_CHILD',
         'component':'Apollo audio manager common-data callback and type8 child',
         'sources':[str(s.relative_to(root)) for s in srcs],
         'source_sha256':[hashlib.sha256(s.read_bytes()).hexdigest() for s in srcs],
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':[hashlib.sha256(native_cb).hexdigest(),hashlib.sha256(native_child).hexdigest()],
         'cases':cases,'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'registry_callback_bodies_complete':10,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Audio message dispatch 0x53c638 and 54 registry callback bodies remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_REGISTRY_AUDM_CALLBACK_CHILD',len(cases),len(after))
