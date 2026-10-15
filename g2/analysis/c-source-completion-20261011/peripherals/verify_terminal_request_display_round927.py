#!/usr/bin/env python3
"""Native/C terminal display request through refresh-wrapper lower-core contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-request-display-round927';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_request_display.c'
obj=out/'terminal_request_display.o'
base=root/'build/c-firmware/td-state-reset-round926/apollo-main-td-state-reset.o'
linked=out/'apollo-main-terminal-request-display.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x5e4784-0x438000:0x5e4788-0x438000],'little')==0x20074a90
native=blob[0x5e43d2-0x438000:0x5e444c-0x438000]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_terminal_display_queue_handle;
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
int32_t audio_uart_master_request_core_464772(uint32_t a,const void*b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_request_display',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native_hooks={0x45a568:'role',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compact',0x464772:'core'}
 compiled_hooks={syms['audio_uart_device_role_get']&~1:'role',syms['audio_log_flags']&~1:'flags',syms['audio_log_extended']&~1:'extended',syms['compressed_log_output']&~1:'compact',syms['audio_uart_master_request_core_464772']&~1:'core'}
 def run(compiled,role,queue,event,value,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  queue_addr=syms['audio_terminal_display_queue_handle'] if compiled else 0x20074a90
  uc.mem_write(queue_addr,queue.to_bytes(4,'little'))
  hooks=compiled_hooks if compiled else native_hooks
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name=='role':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,role)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    msg=string(word(sp+4))
    args=(word(sp+8),word(sp+12)) if 'REFLASH' in msg else ()
    calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),msg,args))
   elif name=='compact':
    msg=string(r1);args=(r3,word(cpu.reg_read(A.UC_ARM_REG_SP))) if 'REFLASH' in msg else ()
    calls.append((name,r0,msg,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0x66)
   else:
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    payload=(int.from_bytes(uc.mem_read(r1,1),'little'),word(r1+4))
    calls.append((name,r0,payload,r2,r3,word(sp),word(sp+4),word(sp+8)))
    cpu.reg_write(A.UC_ARM_REG_R0,0x55)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,value),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_request_display'] if compiled else 0x5e43d2)|1),0x600000,count=1000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for role in (0,1,2):
  for queue in (0,0x12345678):
   for flags in range(8):
    event=31 if flags%2 else 0x11f
    value=0x12340000|flags
    n=run(False,role,queue,event,value,flags);c=run(True,role,queue,event,value,flags)
    assert n==c,(role,queue,event,value,flags,n,c)
    cases.append((role,queue,event,value,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_request_display'}
assert after-before==set()
receipt={'round':927,'status':'PASS_NATIVE_TERMINAL_REQUEST_DISPLAY','component':'Apollo terminal_request_display 0x5e43d2 with display-refresh 0x464bb2 return contract','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Native stack padding bytes in 8-byte display request are unspecified; C initializes them to zero','Runtime queue handle initialization and final linker placement remain open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
