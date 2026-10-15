#!/usr/bin/env python3
"""Compare ring-connect mutex wrappers with official Apollo execution."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-ring-mutex-round906';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_ring_connect_mutex_5e438e.c'
obj=out/'registry_ring_connect_mutex_5e438e.o'
base=root/'build/c-firmware/registry-callback-round905/apollo-main-registry-ring-connect.o'
linked=out/'apollo-main-registry-ring-mutex.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x5e4768-0x438000:0x5e476c-0x438000],'little')==0x20074a84
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_registry_ring_connect_mutex_handle;
uint32_t audio_registry_ring_connect_mutex_init_5e4326(void){return 0;}
int32_t audio_file_mutex_acquire(void*a,uint32_t b)
{(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_registry_ring_connect_enter_5e438e',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'init':'audio_registry_ring_connect_mutex_init_5e4326',
        'take':'audio_file_mutex_acquire',
        'give':'audio_file_mutex_release'}
 native_addrs={'init':0x5e4326,'take':0x4497b6,'give':0x44981c}
 def run(compiled,entry,handle,init_result,take_result):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x110000)
  cell=syms['audio_registry_ring_connect_mutex_handle'] if compiled else 0x20074a84
  uc.mem_write(cell,handle.to_bytes(4,'little'))
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items()}
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   calls.append((name,) if name=='init' else (name,r0,r1) if name=='take' else (name,r0))
   if name=='init':cpu.reg_write(A.UC_ARM_REG_R0,init_result)
   if name=='take':cpu.reg_write(A.UC_ARM_REG_R0,take_result)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  pc=(syms['audio_registry_ring_connect_enter_5e438e'] if entry=='enter' else
      syms['audio_registry_ring_connect_leave_5e43be']) if compiled else (
      0x5e438e if entry=='enter' else 0x5e43be)
  for reg,val in ((A.UC_ARM_REG_R0,0x12345678),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(pc|1,0x600000,count=500)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_SP)
 cases=[]
 for entry,handle,init_result,take_result in [('enter',0,1,0),('enter',0,0,0),
                                               ('enter',0,0,2),('enter',0x1234,0,0),
                                               ('enter',0x1234,0,2),('leave',0,0,0),
                                               ('leave',0x1234,0,0)]:
  n=run(False,entry,handle,init_result,take_result)
  c=run(True,entry,handle,init_result,take_result)
  if entry=='leave':n=(n[0],n[2]);c=(c[0],c[2])
  assert n==c,(entry,handle,init_result,take_result,n,c)
  cases.append({'entry':entry,'handle':handle,'init_result':init_result,
                'take_result':take_result,'calls':len(n[0])})
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_registry_ring_connect_enter_5e438e','audio_registry_ring_connect_leave_5e43be'}
assert after-before=={'audio_registry_ring_connect_mutex_init_5e4326',
                      'audio_registry_ring_connect_mutex_handle'}
receipt={'round':906,'status':'PASS_NATIVE_REGISTRY_RING_MUTEX_WRAPPERS',
 'component':'Apollo ring-connect entry and exit mutex wrappers',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_entries':['0x5e438e','0x5e43be'],'cases':cases,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Mutex init/take/give providers and handle RAM owner remain open',
          'Three ring-connect callback children, 49 registry callback bodies, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
