#!/usr/bin/env python3
"""Native/compiled-C async system-alert packet and submit paths."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-command-round893';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_command_45a8ee.c'
obj=out/'system_alert_command_45a8ee.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x45a8ee-0x438000:0x45a9e6-0x438000]
assert hashlib.sha256(native).hexdigest()=='a54f061e03f4274254e2eb39ab777c1544220a799a02737c2c2ee199252c5309'
assert int.from_bytes(blob[0x45b148-0x438000:0x45b14c-0x438000],'little')==0x45a80b
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_system_alert_async_callback_45a80a(uint32_t a,void*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
void *codec_allocate(uint32_t a){(void)a;return 0;}
void audio_file_heap_free(void *a){(void)a;}
void *audio_queue_copy_bytes(void *a,const void *b,uint32_t n){(void)b;(void)n;return a;}
uint32_t audio_uart_timeout_submit(void(*a)(uint32_t,void*,uint32_t,uint32_t),uint32_t b,
                                   void*c,uint32_t d,uint32_t e)
{(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_command_45a8ee',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,alloc,submit_status,flags,length):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(0x20076000,b'ABCDEF')
  uc.mem_write(0x20077000,b'\xa5'*16)
  native_addrs={'alloc':0x474cd2,'free':0x474d16,'copy':0x439be4,'submit':0x491184,
                'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'alloc':'codec_allocate','free':'audio_file_heap_free',
         'copy':'audio_queue_copy_bytes','submit':'audio_uart_timeout_submit',
         'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='alloc':calls.append(('alloc',r0));cpu.reg_write(A.UC_ARM_REG_R0,0x20077000 if alloc else 0)
   elif op=='free':calls.append(('free',r0))
   elif op=='copy':
    calls.append(('copy',r0,r1,r2));cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
    cpu.reg_write(A.UC_ARM_REG_R0,r0)
   elif op=='submit':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    fifth=int.from_bytes(cpu.mem_read(sp,4),'little')
    callback=(0x45a80b if not compiled else syms['audio_system_alert_async_callback_45a80a']|1)
    assert r0==callback,(compiled,hex(r0),hex(callback))
    calls.append(('submit',r1,r2,r3,fifth,bytes(cpu.mem_read(r2,r3))))
    cpu.reg_write(A.UC_ARM_REG_R0,submit_status)
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    tail=(vals[2],) if vals[0]==212 else ()
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),*tail))
   elif op=='compact':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    tail=(r3,) if r0==0x08400000 else ()
    calls.append(('compact',r0,string(r1),string(r2),*tail))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,33),(A.UC_ARM_REG_R1,0x20076000),
                  (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_R3,0x87654321),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_system_alert_command_45a8ee'] if compiled else 0x45a8ee)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(0x20077000,10))
 cases=[]
 for alloc,submit_status,flags,length in ((False,0,0,0),(False,0,7,3),
                                           (True,0,0,0),(True,0,7,3),
                                           (True,1,0,3),(True,1,7,3)):
  n=run(False,alloc,submit_status,flags,length)
  c=run(True,alloc,submit_status,flags,length)
  assert n==c,(alloc,submit_status,flags,length,n,c)
  cases.append({'alloc':alloc,'submit_status':submit_status,'flags':flags,
                'length':length,'return':n[1],'calls':len(n[0])})

base=root/'build/c-firmware/registry-system-alert-round892/apollo-main-registry-system-alert.o'
linked=out/'apollo-main-system-alert-command.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_system_alert_command_45a8ee'}
assert after-before=={'audio_system_alert_async_callback_45a80a'}
receipt={'round':893,'status':'PASS_NATIVE_SYSTEM_ALERT_COMMAND',
         'component':'Apollo async system-alert packet submitter',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Async callback 0x45a80a and 52 registry callback bodies remain open',
                  'Final placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_SYSTEM_ALERT_COMMAND',len(cases),len(after))
