#!/usr/bin/env python3
"""Native/C Apollo terminal session-list callback at child-call boundaries."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-session-list-round953';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e9c78.c'
obj=out/'terminal_command_5e9c78.o'
base=root/'build/c-firmware/terminal-session-matches-round952/apollo-main-terminal-session-matches.o'
linked=out/'apollo-main-terminal-session-list.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e9c78-0x438000:0x5e9e62-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
uint32_t audio_td_counter_b_get(void){return 0;}
uint8_t audio_td_flag_b_get(void){return 0;}
void audio_td_state_sync(const void*p){(void)p;}
uint8_t *audio_td_state_ptr_alias1(void){return (uint8_t*)0;}
uint8_t audio_ux_get_system_ble_status(void){return 0;}
uint8_t audio_td_has_active_session(void){return 0;}
uint8_t audio_terminal_state_is_processing(uint32_t x){(void)x;return 0;}
uint32_t audio_td_bind_temp_session_response_timer(uint32_t x){(void)x;return 0;}
void audio_terminal_apply_session_id_changed(uint32_t x,uint8_t y){(void)x;(void)y;}
uint8_t audio_terminal_refresh_session_list_if_visible(void){return 0;}
uint16_t audio_td_current_session_index(void){return 0;}
uint32_t audio_terminal_request_display(uint8_t x,uint32_t y){(void)x;(void)y;return 0;}
void audio_terminal_log_session_list_items(const void*p){(void)p;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e9c78',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'counter':'audio_td_counter_b_get','flag':'audio_td_flag_b_get','sync':'audio_td_state_sync','state':'audio_td_state_ptr_alias1','ble':'audio_ux_get_system_ble_status','active':'audio_td_has_active_session','processing':'audio_terminal_state_is_processing','bind':'audio_td_bind_temp_session_response_timer','apply':'audio_terminal_apply_session_id_changed','refresh':'audio_terminal_refresh_session_list_if_visible','index':'audio_td_current_session_index','display':'audio_terminal_request_display','items':'audio_terminal_log_session_list_items','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'counter':0x5973dc,'flag':0x59758e,'sync':0x5977ce,'state':0x597344,'ble':0x47d8ce,'active':0x5973b2,'processing':0x5e8294,'bind':0x5978ee,'apply':0x5e8346,'refresh':0x5e8208,'index':0x5ecafa,'display':0x5e43d2,'items':0x5e9b84,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 payload_addr=0x20010000;state_addr=0x2010fd20
 def run(compiled,present,previous,current,previous_flag,connected,active,processing,refresh,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  p=bytearray(32);p[:4]=(0x1234).to_bytes(4,'little');p[4:8]=(0x5678).to_bytes(4,'little');p[8:10]=(3).to_bytes(2,'little')
  uc.mem_write(payload_addr,bytes(p));uc.mem_write(state_addr+0xa1d8,bytes([2 if connected else 1]))
  uc.mem_write(syms['audio_terminal_ui_mode'] if compiled else 0x2006e345,bytes([2 if processing else 5]))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[];counter_calls=0
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   nonlocal counter_calls
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='counter':
    calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,previous if counter_calls==0 else current);counter_calls+=1
   elif name=='flag':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,previous_flag)
   elif name=='sync':calls.append((name,r0-payload_addr))
   elif name=='state':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,state_addr)
   elif name=='ble':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,1 if connected else 0)
   elif name=='active':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,active)
   elif name=='processing':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,processing)
   elif name=='bind':calls.append((name,r0))
   elif name=='apply':calls.append((name,r0,r1&255))
   elif name=='refresh':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,refresh)
   elif name=='index':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,9)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='items':calls.append((name,r0-payload_addr))
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    line=word(sp)
    args=(word(sp+8),word(sp+12),word(sp+16),word(sp+20)) if line==722 else (word(sp+8),word(sp+12),word(sp+16),word(sp+20),word(sp+24))
    calls.append((name,r0,string(r1),string(r2),string(r3),line,string(word(sp+4)),args))
   else:
    fmt=string(r1)
    args=(r3,word(sp),word(sp+4),word(sp+8)) if 'current_changed=1' in fmt else (r3,word(sp),word(sp+4),word(sp+8),word(sp+12))
    calls.append((name,r0,fmt,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload_addr if present else 0),(A.UC_ARM_REG_R1,0xaaaa),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e9c78'] if compiled else 0x5e9c78)|1),0x600000,count=1500)
  return (uc.reg_read(A.UC_ARM_REG_R0),tuple(calls))
 cases=[]
 for present in (False,True):
  for previous,current in ((0,0),(0,0x1000),(0x1000,0),(0x1000,0x1000),(0x1000,0x2000)):
   for previous_flag in (0,1):
    for connected,active,processing in ((0,0,0),(1,0,0),(1,1,0),(1,1,1)):
     for refresh in (0,1):
      for flags in (0,1,2,4,7):
       args=(present,previous,current,previous_flag,connected,active,processing,refresh,flags)
       n=run(False,*args);c=run(True,*args)
       assert n==c,(args,n,c)
       cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e9c78'}
assert after-before=={'audio_td_flag_b_get','audio_td_state_sync','audio_td_bind_temp_session_response_timer','audio_terminal_refresh_session_list_if_visible','audio_terminal_log_session_list_items'}
receipt={'round':953,'status':'PASS_NATIVE_TERMINAL_SESSION_LIST','component':'Apollo terminal_action_session_list 0x5e9c78','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C child/log call order, changed/current selector branches and return code','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Five child routines newly explicit','3 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
