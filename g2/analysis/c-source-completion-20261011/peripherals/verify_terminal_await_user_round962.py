#!/usr/bin/env python3
"""Native/C Apollo await-user routing, RAM and logging contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-await-user-round962';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_handle_session_await_user.c'
obj=out/'terminal_handle_session_await_user.o'
base=root/'build/c-firmware/td-record-timer-clear-round961/apollo-main-td-record-timer-clear.o'
linked=out/'apollo-main-terminal-await-user.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e84a8-0x438000:0x5e873e-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
uint32_t audio_terminal_display_queue_handle;
uint32_t audio_terminal_runtime_saved_session;
uint8_t audio_terminal_runtime_flag_277;
uint8_t audio_terminal_runtime_flag_27f;
uint32_t audio_td_counter_b_get(void){return 0;}
void audio_td_dismiss_query_notification(uint32_t x){(void)x;}
uint8_t audio_td_session_marked(uint32_t x){(void)x;return 0;}
uint8_t audio_terminal_refresh_session_list_if_visible(void){return 0;}
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t audio_system_alert_command_45a8ee(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint8_t audio_terminal_state_allows_runtime_event(uint32_t x){(void)x;return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_handle_session_await_user',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'counter':'audio_td_counter_b_get','dismiss':'audio_td_dismiss_query_notification','marked':'audio_td_session_marked','refresh':'audio_terminal_refresh_session_list_if_visible','role':'audio_uart_device_role_get','alert':'audio_system_alert_command_45a8ee','allowed':'audio_terminal_state_allows_runtime_event','display':'audio_terminal_request_display','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'counter':0x5973dc,'dismiss':0x5974d4,'marked':0x597544,'refresh':0x5e8208,'role':0x45a568,'alert':0x45a8ee,'allowed':0x5e8276,'display':0x5e43d2,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,session,current_match,mode,queue,marked,refresh,role,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  cells={'audio_terminal_ui_mode':(0x2006e345,mode,1),'audio_terminal_display_queue_handle':(0x20074a90,queue,4),'audio_terminal_runtime_saved_session':(0x2006e358,0xabcdef,4),'audio_terminal_runtime_flag_277':(0x2006e347,0x7a,1),'audio_terminal_runtime_flag_27f':(0x2006e34f,0x7b,1)}
  for name,(native_addr,value,width) in cells.items():uc.mem_write(syms[name] if compiled else native_addr,value.to_bytes(width,'little'))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='counter':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,session if current_match else 0x12345678)
   elif name=='dismiss':calls.append((name,r0))
   elif name=='marked':calls.append((name,r0));cpu.reg_write(A.UC_ARM_REG_R0,marked)
   elif name=='refresh':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,refresh)
   elif name=='role':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,role)
   elif name=='alert':calls.append((name,r0,r1,r2,r3));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='allowed':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,1 if mode in (0,2,7,11,12) else 0)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    line=word(sp)
    args=() if line==170 else (word(sp+8),word(sp+12)) if line==208 else (word(sp+8),)
    calls.append((name,r0,string(r1),string(r2),string(r3),line,string(word(sp+4)),args))
   else:
    fmt=string(r1)
    args=() if 'without session id' in fmt else (r3,word(sp)) if 'in state=' in fmt else (r3,)
    calls.append((name,r0,fmt,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,session),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_handle_session_await_user'] if compiled else 0x5e84a8)|1),0x600000,count=1200)
  state=tuple(int.from_bytes(uc.mem_read(syms[name] if compiled else addr,width),'little') for name,(addr,_,width) in cells.items() if name in ('audio_terminal_runtime_saved_session','audio_terminal_runtime_flag_277','audio_terminal_runtime_flag_27f'))
  return state,tuple(calls)
 cases=[]
 for session in (0,0x1000):
  for current_match in (False,True):
   for mode in (0,2,5,7,11,12):
    for queue in (0,0x1234):
     for marked in (0,1):
      for refresh in (0,1):
       for role in (0,1):
        for flags in (0,1,2,4,7):
         args=(session,current_match,mode,queue,marked,refresh,role,flags)
         n=run(False,*args);c=run(True,*args)
         assert n==c,(args,n,c)
         cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_handle_session_await_user'}
assert after-before=={'audio_td_dismiss_query_notification'}
receipt={'round':962,'status':'PASS_NATIVE_TERMINAL_AWAIT_USER','component':'Apollo terminal_handle_session_await_user 0x5e84a8','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C routing, child/log call order and three terminal RAM cells','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Dismiss-query child 0x5974d4 remains open','2 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
