#!/usr/bin/env python3
"""Native/compiled-C Quicklist registry callback branch and call traces."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-quicklist-round890';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_callback_4ffb38.c'
obj=out/'registry_callback_4ffb38.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x4ffb38-0x438000:0x4ffba6-0x438000]
assert native[:2].hex()=='7fb5' and native[-2:].hex()=='70bd'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_quicklist_data_mutex_init_4ffa70(void){}
uint32_t audio_quicklist_frame_process_55894c(const void *a,uint16_t b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_decode_558b3c(void){return 0;}
void audio_quicklist_refresh_4f5e84(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_4ffb38',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,event,frame_result,decode_result,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  native_addrs={'mutex':0x4ffa70,'frame':0x55894c,'decode':0x558b3c,
                'refresh':0x4f5e84,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'mutex':'audio_quicklist_data_mutex_init_4ffa70',
         'frame':'audio_quicklist_frame_process_55894c',
         'decode':'audio_quicklist_decode_558b3c',
         'refresh':'audio_quicklist_refresh_4f5e84','flags':'audio_log_flags',
         'extended':'audio_log_extended','compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='mutex':calls.append(('mutex',))
   elif op=='frame':calls.append(('frame',r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,frame_result)
   elif op=='decode':calls.append(('decode',));cpu.reg_write(A.UC_ARM_REG_R0,decode_result)
   elif op=='refresh':calls.append(('refresh',))
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),vals[2]))
   elif op=='compact':calls.append(('compact',r0,string(r1),string(r2),r3))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,0x20076000),
                  (A.UC_ARM_REG_R2,0x12345),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_uart_registry_callback_4ffb38'] if compiled else 0x4ffb38)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for event,frame,decode,flags in ((0,0,0,0),(0,1,0,7),(0,0,1,7),
                                  (1,0,0,0),(2,0,0,2),(3,0,0,4),(0xffffffff,0,0,7)):
  n=run(False,event,frame,decode,flags);c=run(True,event,frame,decode,flags)
  assert n==c,(event,frame,decode,flags,n,c)
  cases.append({'event':event,'frame_result':frame,'decode_result':decode,
                'flags':flags,'calls':len(n[0])})

base=root/'build/c-firmware/aud-dispatch-bridge-round889/apollo-main-aud-dispatch-bridge.o'
linked=out/'apollo-main-registry-quicklist.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_registry_callback_4ffb38'}
assert after-before=={'audio_quicklist_data_mutex_init_4ffa70','audio_quicklist_frame_process_55894c',
                      'audio_quicklist_decode_558b3c','audio_quicklist_refresh_4f5e84'}
receipt={'round':890,'status':'PASS_NATIVE_REGISTRY_QUICKLIST_CALLBACK',
         'component':'Apollo Quicklist common-data callback',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'cases':cases,'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_child_imports':sorted(after-before),
         'registry_callback_bodies_complete':11,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Four Quicklist child bodies and 53 registry callback bodies remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_REGISTRY_QUICKLIST_CALLBACK',len(cases),len(after))
