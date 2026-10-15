#!/usr/bin/env python3
"""Native/C session-ID application composition and log dispatch."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-apply-session-round933';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_apply_session_id_changed.c'
obj=out/'terminal_apply_session_id_changed.o'
base=root/'build/c-firmware/td-current-index-round932/apollo-main-td-current-index.o'
linked=out/'apollo-main-terminal-apply-session.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e8346-0x438000:0x5e84a8-0x438000]
assert hashlib.sha256(native).hexdigest()=='37708a4237eb86cbc6c7e12932f9b4212a121475eb02f223be1bf99488bd28d3'
assert int.from_bytes(blob[0x5e8c04-0x438000:0x5e8c08-0x438000],'little')+0x275==0x2006e345
symbols={'bind':'audio_td_session_bind_store','cached':'audio_terminal_cached_session_status','flag':'audio_td_flag_set_with_reset','output':'audio_terminal_reset_output_tracking','ring':'audio_td_ring_reset_wrapper','notify':'audio_td_notify_state_clear','session_clear':'audio_td_session_struct_clear','record':'audio_td_record_status_set','active':'audio_td_has_active_session','index':'audio_td_current_session_index','display':'audio_terminal_request_display','status_name':'audio_terminal_session_status_name','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
native_addrs={'bind':0x5979b2,'cached':0x5e830c,'flag':0x597572,'output':0x5e8178,'ring':0x597108,'notify':0x597110,'session_clear':0x597124,'record':0x597464,'active':0x5973b2,'index':0x5ecafa,'display':0x5e43d2,'status_name':0x5e82a4,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_td_session_bind_store(uint32_t a){(void)a;}
uint8_t audio_terminal_cached_session_status(uint32_t a){(void)a;return 0;}
void audio_td_flag_set_with_reset(uint8_t a){(void)a;}
void audio_terminal_reset_output_tracking(void){}
void audio_td_ring_reset_wrapper(void){}
void audio_td_notify_state_clear(void){}
void audio_td_session_struct_clear(void){}
void audio_td_record_status_set(uint32_t a,uint8_t b){(void)a;(void)b;}
uint8_t audio_td_has_active_session(void){return 0;}
uint16_t audio_td_current_session_index(void){return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
const char *audio_terminal_session_status_name(uint32_t a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_apply_session_id_changed',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,session,reset,active,mode,status,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(syms['audio_terminal_ui_mode'] if compiled else 0x2006e345,bytes([mode]))
  uc.mem_write(0x20078000,b'STATUS\0')
  hooks={((syms[symbols[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name in ('bind','cached'):calls.append((name,r0));cpu.reg_write(A.UC_ARM_REG_R0,status if name=='cached' else 0)
   elif name=='flag':calls.append((name,r0&255))
   elif name in ('output','ring','notify','session_clear'):calls.append((name,))
   elif name=='record':calls.append((name,r0,r1&255))
   elif name=='active':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,active)
   elif name=='index':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0xfffe)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0x77)
   elif name=='status_name':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,0x20078000)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(word(sp+4))
    args=(word(sp+8),word(sp+12),string(word(sp+16))) if 'status=%d' in msg else ()
    calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),msg,args))
   else:
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(r1)
    args=(r3,word(sp),string(word(sp+4))) if 'status=%d' in msg else ()
    calls.append((name,r0,msg,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0x66)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,session),(A.UC_ARM_REG_R1,reset),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_apply_session_id_changed'] if compiled else 0x5e8346)|1),0x600000,count=1000)
  return calls
 cases=[]
 for session in (0,0x1234):
  for reset in (0,1):
   for active in (0,1):
    for mode in (0,11):
     for status in (0,2,5):
      for flags in range(8):
       n=run(False,session,reset,active,mode,status,flags)
       c=run(True,session,reset,active,mode,status,flags)
       assert n==c,(session,reset,active,mode,status,flags,n,c)
       cases.append((session,reset,active,mode,status,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_apply_session_id_changed'}
assert after-before==set()
receipt={'round':933,'status':'PASS_NATIVE_TERMINAL_APPLY_SESSION','component':'Apollo terminal_apply_session_id_changed 0x5e8346','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C direct-child and log call-order differential; child body RAM effects verified in earlier rounds','native_ui_mode':'0x2006e345','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Final linker placement and runtime initialization of UI mode and terminal state remain open','7 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
