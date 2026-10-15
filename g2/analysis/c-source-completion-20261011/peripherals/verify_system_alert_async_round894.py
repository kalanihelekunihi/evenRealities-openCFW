#!/usr/bin/env python3
"""Native/compiled-C async startup callback effects and logging."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-async-round894';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_async_callback_45a80a.c'
obj=out/'system_alert_async_callback_45a80a.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x45a80a-0x438000:0x45a8ee-0x438000]
assert hashlib.sha256(native).hexdigest()=='38004837ceadb5a37143728dc97cc12ca729a9217cffec543b27724efb50542b'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_uart_task_delay(uint32_t a){(void)a;}
void audio_uart_master_display_start(uint32_t a,const void*b,uint16_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
void audio_file_heap_free(void *a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_async_callback_45a80a',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,has_packet,length,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(0x20077000,b'\x21\x43\x65\x87ABCDEF')
  native_addrs={'delay':0x454b4c,'master':0x464b2e,'free':0x474d16,
                'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'delay':'audio_uart_task_delay','master':'audio_uart_master_display_start',
         'free':'audio_file_heap_free','flags':'audio_log_flags',
         'extended':'audio_log_extended','compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='delay':calls.append(('delay',r0))
   elif op=='master':calls.append(('master',r0,r1,r2,r3,
                                   bytes(cpu.mem_read(r1,r2)) if r1 and r2 else b''))
   elif op=='free':calls.append(('free',r0))
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(4)]
    extra=tuple(vals[2:4]) if vals[0]==200 else ()
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),*extra))
   elif op=='compact':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    extra=(r3,int.from_bytes(cpu.mem_read(sp,4),'little')) if r0==0x0c800000 else ()
    calls.append(('compact',r0,string(r1),string(r2),*extra))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x12345),
                  (A.UC_ARM_REG_R1,0x20077000 if has_packet else 0),
                  (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_R3,0xdeadbeef),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_system_alert_async_callback_45a80a'] if compiled else 0x45a80a)|1),
               0x600000,count=10000)
  return calls
 cases=[]
 for packet,length,flags in ((False,0,0),(False,0,7),(True,4,0),
                             (True,4,7),(True,7,2),(True,7,4)):
  n=run(False,packet,length,flags);c=run(True,packet,length,flags)
  assert n==c,(packet,length,flags,n,c)
  cases.append({'packet':packet,'length':length,'flags':flags,'calls':len(n)})

base=root/'build/c-firmware/system-alert-command-round893/apollo-main-system-alert-command.o'
linked=out/'apollo-main-system-alert-async.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_system_alert_async_callback_45a80a'} and not after-before
receipt={'round':894,'status':'PASS_NATIVE_SYSTEM_ALERT_ASYNC_CALLBACK',
         'component':'Apollo async display startup work callback',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'registry_callback_bodies_complete':12,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['52 registry callback bodies and other selected Apollo imports remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_SYSTEM_ALERT_ASYNC_CALLBACK',len(cases),len(after))
