#!/usr/bin/env python3
"""Native/C Apollo host-status callback composition and state transition."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-host-status-round938';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e8c48.c'
obj=out/'terminal_command_5e8c48.o'
base=root/'build/c-firmware/terminal-host-helpers-round937/apollo-main-terminal-host-helpers.o'
linked=out/'apollo-main-terminal-host-status.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e8c48-0x438000:0x5e8e34-0x438000]
assert hashlib.sha256(native).hexdigest()=='16af2b672b6cc4c2ac50f3cd94689287a4790ecc880736184ea0184f7e6bb96d'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
const char *audio_terminal_host_status_name(uint32_t a){(void)a;return 0;}
uint8_t *audio_td_state_ptr_alias2(void){return 0;}
void audio_td_notify_state_clear(void){}
void audio_td_session_struct_clear(void){}
uint8_t audio_td_has_active_session(void){return 0;}
uint32_t audio_td_counter_b_get(void){return 0;}
uint8_t audio_terminal_state_is_processing(uint32_t a){(void)a;return 0;}
void audio_terminal_apply_session_id_changed(uint32_t a,uint8_t b){(void)a;(void)b;}
uint16_t audio_td_current_session_index(void){return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint8_t audio_ux_get_system_ble_status(void){return 0;}
void audio_terminal_request_runtime_event_if_allowed(uint32_t a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e8c48',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'name':'audio_terminal_host_status_name','state':'audio_td_state_ptr_alias2','notify':'audio_td_notify_state_clear','clear':'audio_td_session_struct_clear','active':'audio_td_has_active_session','session':'audio_td_counter_b_get','processing':'audio_terminal_state_is_processing','apply':'audio_terminal_apply_session_id_changed','index':'audio_td_current_session_index','display':'audio_terminal_request_display','ble':'audio_ux_get_system_ble_status','runtime':'audio_terminal_request_runtime_event_if_allowed','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'name':0x5e82e6,'state':0x59734a,'notify':0x597110,'clear':0x597124,'active':0x5973b2,'session':0x5973dc,'processing':0x5e8294,'apply':0x5e8346,'index':0x5ecafa,'display':0x5e43d2,'ble':0x47d8ce,'runtime':0x5e873e,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,present,previous,next_status,active,mode,session,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(0x20076000,bytes([next_status]));uc.mem_write(0x20078000,b'HOST_NAME\0')
  uc.mem_write(0x20078000+0xa1d8,bytes([previous]))
  uc.mem_write(syms['audio_terminal_ui_mode'] if compiled else 0x2006e345,bytes([mode]))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name=='name':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,0x20078000)
   elif name=='state':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0x20078000)
   elif name in ('notify','clear'):calls.append((name,))
   elif name=='active':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,active)
   elif name=='session':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,session)
   elif name=='processing':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,1 if mode in (1,2,3) else 0)
   elif name=='apply':calls.append((name,r0,r1&255))
   elif name=='index':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0xfffe)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0x77)
   elif name=='ble':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,2)
   elif name=='runtime':calls.append((name,r0&255))
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(word(sp+4))
    if 'host_status=%d' in msg:args=(word(sp+8),string(word(sp+12)))
    elif 'session=%lu' in msg:args=(word(sp+8),)
    else:args=()
    calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),msg,args))
   else:
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(r1)
    if 'host_status=%d' in msg:args=(r3,string(word(sp)))
    elif 'session=%lu' in msg:args=(r3,)
    else:args=()
    calls.append((name,r0,msg,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0x66)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x20076000 if present else 0),(A.UC_ARM_REG_R1,0x1234),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e8c48'] if compiled else 0x5e8c48)|1),0x600000,count=1500)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(0x20078000+0xa1d8,1))
 cases=[]
 for present,previous,next_status,active,mode,session,flags in [(False,0,0,0,0,0,0)]+[(True,p,n,a,m,s,f) for p in (0,1,2,3) for n in (0,1,2,3) for a in (0,1) for m in (0,2) for s in (0,0x1234) for f in (0,2,5,7)]:
  n=run(False,present,previous,next_status,active,mode,session,flags)
  c=run(True,present,previous,next_status,active,mode,session,flags)
  assert n==c,(present,previous,next_status,active,mode,session,flags,n,c)
  cases.append((present,previous,next_status,active,mode,session,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e8c48'}
assert after-before=={'audio_ux_get_system_ble_status','audio_terminal_request_runtime_event_if_allowed'}
receipt={'round':938,'status':'PASS_NATIVE_TERMINAL_HOST_STATUS','component':'Apollo terminal_action_host_status 0x5e8c48','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C direct-child/log call-order and host-state byte differential','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'terminal_handlers_compiled':7,'terminal_handlers_total':12,'whole_image_complete':False,'hardware_proof':False,'gates':['UX_GetSystemBLEStatus 0x47d8ce and runtime-event helper 0x5e873e remain open','5 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
