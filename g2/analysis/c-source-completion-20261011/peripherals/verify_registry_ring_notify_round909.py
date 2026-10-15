#!/usr/bin/env python3
"""Native/C comparison for Terminal comm-response notification."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-ring-notify-round909';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_ring_connect_notify_5ceaec.c'
obj=out/'registry_ring_connect_notify_5ceaec.o'
base=root/'build/c-firmware/registry-ring-state-round908/apollo-main-registry-ring-state.o'
linked=out/'apollo-main-registry-ring-notify.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ceaec-0x438000:0x5ceba2-0x438000]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
uint32_t audio_terminal_send_message_5ce7c4(uint32_t a,uint32_t b,const void*c,uint32_t d,uint32_t e)
{(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_registry_ring_connect_notify_5ceaec',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'flags':'audio_log_flags','extended':'audio_log_extended',
        'compact':'compressed_log_output','send':'audio_terminal_send_message_5ce7c4'}
 native_addrs={'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e,'send':0x5ce7c4}
 def run(compiled,present,state,sequence,flags_value,send_result):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  ptr=0x20076000 if present else 0
  if present:uc.mem_write(ptr,bytes([state]))
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items()}
  def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='flags':calls.append(('flags',));cpu.reg_write(A.UC_ARM_REG_R0,flags_value)
   elif name=='extended':
    calls.append(('extended',r0,string(r1),string(r2),string(r3),word(sp),
                  string(word(sp+4)),word(sp+8) if present else None,
                  word(sp+12) if present else None))
   elif name=='compact':
    calls.append(('compact',r0,string(r1),string(r2),r3 if present else None,
                  word(sp) if present else None))
   else:
    calls.append(('send',r0,r1,r2==ptr,r3,word(sp)))
    cpu.reg_write(A.UC_ARM_REG_R0,send_result)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,ptr),(A.UC_ARM_REG_R1,sequence),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_registry_ring_connect_notify_5ceaec'] if compiled else 0x5ceaec)|1),
               0x600000,count=1000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for present,state,sequence,flags_value in [(0,0,0,0),(0,0,0,7),(1,0,0,0),
                                              (1,1,0x23,2),(1,2,0xff,1),(1,3,0x123,4),
                                              (1,0xff,0x42,7)]:
  n=run(False,present,state,sequence,flags_value,0x77)
  c=run(True,present,state,sequence,flags_value,0x77)
  assert n==c,(present,state,sequence,flags_value,n,c)
  cases.append({'present':present,'state':state,'sequence':sequence,
                'flags':flags_value,'calls':len(n[0]),'return':n[1]})
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_registry_ring_connect_notify_5ceaec'}
assert after-before=={'audio_terminal_send_message_5ce7c4'}
receipt={'round':909,'status':'PASS_NATIVE_REGISTRY_RING_NOTIFY',
 'component':'Apollo Terminal comm-response notification 0x5ceaec',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Terminal send child 0x5ce7c4 remains open',
          'Ring-connect parse/check children and buffer, 49 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
