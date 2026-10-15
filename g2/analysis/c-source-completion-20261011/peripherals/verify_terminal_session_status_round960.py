#!/usr/bin/env python3
"""Native/C Apollo terminal session-status callback child/log/state contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-session-status-round960';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e9064.c'
obj=out/'terminal_command_5e9064.o'
base=root/'build/c-firmware/terminal-list-items-round959/apollo-main-terminal-list-items.o'
linked=out/'apollo-main-terminal-session-status.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e9064-0x438000:0x5e9312-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
uint32_t audio_terminal_runtime_saved_session;
struct audio_terminal_output_tracking {uint8_t active;uint8_t reserved[3];uint32_t count;};
struct audio_terminal_output_tracking audio_terminal_output_tracking;
uint32_t audio_terminal_session_switch_tick;
uint32_t audio_terminal_message_session_matches(uint32_t a,const char*b){(void)a;(void)b;return 0;}
const char *audio_terminal_session_status_name(uint32_t x){(void)x;return "STATUS";}
void audio_td_record_status_set(uint32_t a,uint8_t b){(void)a;(void)b;}
void audio_terminal_handle_session_await_user(uint32_t a){(void)a;}
uint32_t audio_td_counter_b_get(void){return 0;}
void audio_terminal_reset_output_tracking(void){}
void audio_td_record_timer_clear(uint32_t a){(void)a;}
void audio_td_ring_reset_wrapper(void){}
void audio_td_notify_state_clear(void){}
void audio_td_session_struct_clear(void){}
uint8_t audio_terminal_refresh_session_list_if_visible(void){return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e9064',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'match':'audio_terminal_message_session_matches','status_name':'audio_terminal_session_status_name','set':'audio_td_record_status_set','await':'audio_terminal_handle_session_await_user','counter':'audio_td_counter_b_get','reset':'audio_terminal_reset_output_tracking','timer':'audio_td_record_timer_clear','ring':'audio_td_ring_reset_wrapper','notify':'audio_td_notify_state_clear','clear':'audio_td_session_struct_clear','refresh':'audio_terminal_refresh_session_list_if_visible','display':'audio_terminal_request_display','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'match':0x5e818a,'status_name':0x5e82a4,'set':0x597464,'await':0x5e84a8,'counter':0x5973dc,'reset':0x5e8178,'timer':0x597652,'ring':0x597108,'notify':0x597110,'clear':0x597124,'refresh':0x5e8208,'display':0x5e43d2,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 payload_addr=0x20010000;status_text=0x2001f000
 def run(compiled,present,status,current_match,sync_match,mode,saved_match,active,refresh,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  p=bytearray(16);p[0]=status;p[4:8]=(0x1234).to_bytes(4,'little')
  uc.mem_write(payload_addr,bytes(p));uc.mem_write(status_text,b'STATUS\0')
  cells={'audio_terminal_ui_mode':(0x2006e345,mode,1),'audio_terminal_runtime_saved_session':(0x2006e358,0x1234 if saved_match else 0x9876,4),'audio_terminal_output_tracking':(0x2006e364,active,1),'audio_terminal_session_switch_tick':(0x2006e36c,0xaaaa5555,4)}
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
   if name=='match':calls.append((name,r0,string(r1)));cpu.reg_write(A.UC_ARM_REG_R0,sync_match)
   elif name=='status_name':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,status_text)
   elif name=='set':calls.append((name,r0,r1&255))
   elif name in ('await','timer'):calls.append((name,r0))
   elif name=='counter':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0x1234 if current_match else 0x9876)
   elif name in ('reset','ring','notify','clear'):calls.append((name,))
   elif name=='refresh':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,refresh)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    line=word(sp);fmt=string(word(sp+4))
    args=(word(sp+8),word(sp+12),string(word(sp+16))) if line in (436,464) else (word(sp+8),string(word(sp+12))) if line==492 else (word(sp+8),)
    calls.append((name,r0,string(r1),string(r2),string(r3),line,fmt,args))
   else:
    fmt=string(r1)
    args=(r3,word(sp),string(word(sp+4))) if 'status:id=' in fmt or 'cached for inactive' in fmt else (r3,string(word(sp))) if 'skip session status' in fmt else (r3,)
    calls.append((name,r0,fmt,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload_addr if present else 0),(A.UC_ARM_REG_R1,0xaaaa),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e9064'] if compiled else 0x5e9064)|1),0x600000,count=1500)
  tick_addr=syms['audio_terminal_session_switch_tick'] if compiled else 0x2006e36c
  return uc.reg_read(A.UC_ARM_REG_R0),int.from_bytes(uc.mem_read(tick_addr,4),'little'),tuple(calls)
 cases=[]
 for present in (False,True):
  for status in (0,1,2,3,4,5):
   for current_match in (False,True):
    for sync_match in (False,True):
     for mode,saved_match,active in ((0,False,0),(10,False,0),(10,True,0),(10,True,1),(0,False,1)):
      for refresh in (0,1):
       for flags in (0,1,2,4,7):
        args=(present,status,current_match,sync_match,mode,saved_match,active,refresh,flags)
        n=run(False,*args);c=run(True,*args)
        assert n==c,(args,n,c)
        cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e9064'}
assert after-before=={'audio_terminal_handle_session_await_user','audio_td_record_timer_clear'}
receipt={'round':960,'status':'PASS_NATIVE_TERMINAL_SESSION_STATUS','component':'Apollo terminal_action_session_status 0x5e9064','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C sync, await, active/inactive UI paths, child/log call order and sync-gate RAM','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Await-user and record-timer child routines newly explicit','2 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
