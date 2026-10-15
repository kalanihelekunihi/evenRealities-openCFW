#!/usr/bin/env python3
"""Compare native and compiled-C universal-setting receive branch traces."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-child-round885';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_child_466412.c'
obj=out/'registry_child_466412.o'
flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11',
       '-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror']
subprocess.run(['clang',*flags,'-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x466412-0x438000:0x4664fa-0x438000]
assert native[:2].hex()=='7cb5' and native[-2:].hex()=='73bd'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_uart_hand_record[0x30];
uint8_t audio_uart_device_role_get(void){return 0;}
void *audio_queue_copy_bytes(void *a,const void *b,uint32_t n){(void)b;(void)n;return a;}
uint32_t audio_uart_registry_hand_compare_46636c(const uint8_t *a){(void)a;return 0;}
void audio_uart_ring_unpair_publish_hand_4661a6(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_child_466412',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,role,kind,equal,flags_value):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  record=bytearray(range(48));record[0]=kind
  uc.mem_write(0x20076000,bytes(record))
  dst=syms['audio_uart_hand_record'] if compiled else 0x200736d4
  uc.mem_write(dst,b'\xa5'*48)
  names={'role':'audio_uart_device_role_get','copy':'audio_queue_copy_bytes',
         'compare':'audio_uart_registry_hand_compare_46636c',
         'publish':'audio_uart_ring_unpair_publish_hand_4661a6',
         'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output'}
  native_addrs={'role':0x45a568,'copy':0x439be4,'compare':0x46636c,
                'publish':0x4661a6,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def cstring(ptr):
   raw=bytes(uc.mem_read(ptr,160));return raw.split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='role':cpu.reg_write(A.UC_ARM_REG_R0,role)
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags_value)
   elif op=='compare':calls.append(('compare',));cpu.reg_write(A.UC_ARM_REG_R0,equal)
   elif op=='copy':
    calls.append(('copy',r0-dst,r1-0x20076000,r2))
    cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
    cpu.reg_write(A.UC_ARM_REG_R0,r0)
   elif op=='publish':calls.append(('publish',))
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    line=int.from_bytes(cpu.mem_read(sp,4),'little')
    msg=int.from_bytes(cpu.mem_read(sp+4,4),'little')
    calls.append(('extended',r0,cstring(r1),cstring(r2),cstring(r3),line,cstring(msg)))
   elif op=='compact':calls.append(('compact',r0,cstring(r1),cstring(r2)))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  uc.reg_write(A.UC_ARM_REG_R0,0x20076000)
  uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
  uc.reg_write(A.UC_ARM_REG_LR,0x600001)
  uc.emu_start(((syms['audio_uart_registry_child_466412'] if compiled else 0x466412)|1),0x600000,count=10000)
  return calls,bytes(uc.mem_read(dst,48))
 cases=[]
 for role,kind,equal,flags_value in ((2,0,0,0),(2,0,0,7),(1,1,1,0),(1,1,1,7),
                                     (1,1,0,0),(1,1,0,7),(1,0,0,7),(2,1,0,7),(1,2,0,7)):
  n=run(False,role,kind,equal,flags_value)
  c=run(True,role,kind,equal,flags_value)
  assert n==c,(role,kind,equal,flags_value,n,c)
  cases.append({'role':role,'kind':kind,'equal':equal,'log_flags':flags_value,
                'calls':len(n[0]),'saved_sha256':hashlib.sha256(n[1]).hexdigest()})

base=root/'build/c-firmware/registry-hand-compare-round884/apollo-main-registry-hand-compare.o'
linked=out/'apollo-main-registry-child.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_registry_child_466412'} and not after-before
receipt={'round':885,'status':'PASS_NATIVE_REGISTRY_SYNC_CHILD',
         'component':'Apollo universal setting sync receive',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Saved hand record RAM ownership and 56 other registry callback bodies remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_REGISTRY_SYNC_CHILD',len(cases),len(after))
