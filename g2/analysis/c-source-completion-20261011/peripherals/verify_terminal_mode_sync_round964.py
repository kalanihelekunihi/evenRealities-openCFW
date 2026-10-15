#!/usr/bin/env python3
"""Native/C Apollo terminal mode-sync callback child, log and RAM contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-mode-sync-round964';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e8846.c'
obj=out/'terminal_command_5e8846.o'
base=root/'build/c-firmware/td-dismiss-query-round963/apollo-main-td-dismiss-query.o'
linked=out/'apollo-main-terminal-mode-sync.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e8846-0x438000:0x5e8c04-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
uint32_t audio_settings_terminal_mode(void){return 0;}
void audio_settings_terminal_mode_set(uint32_t x){(void)x;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t audio_terminal_send_status_reply(const void*p){(void)p;return 0;}
void audio_input_message_send_id4(uint32_t x){(void)x;}
uint32_t audio_get_running_app_ids(uint32_t*a,uint32_t*b){(void)a;(void)b;return 0;}
uint8_t audio_uart_device_role_get(void){return 0;}
void audio_uart_master_display_stop(uint32_t a,const void*b,uint16_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
void audio_td_state_reset(void){}
void audio_terminal_reset_output_tracking(void){}
void audio_terminal_runtime_event_callback_1(uint32_t x,const void*p){(void)x;(void)p;}
void audio_ble_status_register_callback(void(*p)(uint32_t,const void*)){(void)p;}
void audio_ble_status_unregister_callback(void(*p)(uint32_t,const void*)){(void)p;}
void audio_os_delay(uint32_t x){(void)x;}
void audio_uart_ring_wear_persist_48eb32(uint32_t a,uint32_t b,const void*p){(void)a;(void)b;(void)p;}
uint32_t audio_system_alert_command_45a8ee(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint64_t audio_uart_ring_u64_div_47cc60(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_ble_param_reset_delayed_event(uint32_t x){(void)x;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e8846',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'get':'audio_settings_terminal_mode','set':'audio_settings_terminal_mode_set','zero':'audio_uart_buffer_zero','reply':'audio_terminal_send_status_reply','id4':'audio_input_message_send_id4','apps':'audio_get_running_app_ids','role':'audio_uart_device_role_get','stop':'audio_uart_master_display_stop','td_reset':'audio_td_state_reset','out_reset':'audio_terminal_reset_output_tracking','register':'audio_ble_status_register_callback','unregister':'audio_ble_status_unregister_callback','delay':'audio_os_delay','persist':'audio_uart_ring_wear_persist_48eb32','alert':'audio_system_alert_command_45a8ee','tick':'g2_flashdb_candidate_tick','divide':'audio_uart_ring_u64_div_47cc60','ble_reset':'audio_ble_param_reset_delayed_event','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'get':0x46c630,'set':0x46c63c,'zero':0x43c0e4,'reply':0x5ceba2,'id4':0x5130c0,'apps':0x443504,'role':0x45a568,'stop':0x464c36,'td_reset':0x5970f0,'out_reset':0x5e8178,'register':0x4abcc6,'unregister':0x4abd14,'delay':0x449376,'persist':0x48eb32,'alert':0x45a8ee,'tick':0x4490cc,'divide':0x47cc60,'ble_reset':0x478252,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,present,incoming,current,apps,foreground,background,role,ui,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  payload=0x20010000;uc.mem_write(payload,bytes([incoming]))
  cells={'audio_terminal_ui_mode':(0x2006e345,ui,1),'audio_terminal_mode_sync_pending':(0x2006e344,0x7a,1),'audio_terminal_mode_start_tick':(0x20074a8c,0x100,4)}
  for name,(native_addr,value,width) in cells.items():uc.mem_write(syms[name] if compiled else native_addr,value.to_bytes(width,'little'))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  callback=(syms['audio_terminal_runtime_event_callback_1'] if compiled else 0x5e8815)|1
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='zero':calls.append((name,r1,r2));cpu.mem_write(r0,b'\0'*r1)
   elif name=='get':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,current)
   elif name=='set':calls.append((name,r0))
   elif name=='reply':calls.append((name,bytes(cpu.mem_read(r0,2))));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='id4':calls.append((name,r0))
   elif name=='apps':calls.append((name,));cpu.mem_write(r0,background.to_bytes(4,'little'));cpu.mem_write(r1,foreground.to_bytes(4,'little'));cpu.reg_write(A.UC_ARM_REG_R0,apps)
   elif name=='role':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,role)
   elif name=='stop':calls.append((name,r0,r1,r2,r3))
   elif name in ('td_reset','out_reset'):calls.append((name,))
   elif name in ('register','unregister'):calls.append((name,r0==callback))
   elif name=='delay':calls.append((name,r0))
   elif name=='persist':calls.append((name,r0,r1,word(r2),word(r2+4)));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='alert':calls.append((name,r0,r1,r2,r3));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='tick':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0x140)
   elif name=='divide':calls.append((name,r0,r1,r2,r3));cpu.reg_write(A.UC_ARM_REG_R0,64)
   elif name=='ble_reset':calls.append((name,r0))
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    line=word(sp);args=(word(sp+8),word(sp+12)) if line in (269,287) else (word(sp+8),) if line==309 else ()
    calls.append((name,r0,string(r1),string(r2),string(r3),line,string(word(sp+4)),args))
   else:
    fmt=string(r1);args=(r3,word(sp)) if 'mode_sync recv' in fmt or 'running apps' in fmt else (r3,) if 'startup requested' in fmt else ()
    calls.append((name,r0,fmt,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload if present else 0),(A.UC_ARM_REG_R1,0xaaaa),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e8846'] if compiled else 0x5e8846)|1),0x600000,count=3000)
  state=tuple(int.from_bytes(uc.mem_read(syms[name] if compiled else addr,width),'little') for name,(addr,_,width) in cells.items() if name!='audio_terminal_ui_mode')
  return uc.reg_read(A.UC_ARM_REG_R0),state,tuple(calls)
 cases=[]
 for present in (False,True):
  for incoming in (0,2,255):
   for current in (0,1):
    for apps,foreground,background in ((1,0,0),(0,0,0),(0,0x1234,0),(0,0,0x5678),(0,0x1234,0x5678)):
     for role in (0,1):
      for ui in (0,7):
       for flags in (0,2,5):
        args=(present,incoming,current,apps,foreground,background,role,ui,flags)
        n=run(False,*args);c=run(True,*args)
        assert n==c,(args,n,c)
        cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e8846'}
receipt={'round':964,'status':'PASS_NATIVE_TERMINAL_MODE_SYNC','component':'Apollo terminal_action_mode_sync 0x5e8846','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C enter, exit, unchanged mode child/log order and mode/tick RAM','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'new_imports':sorted(after-before),'whole_image_complete':False,'hardware_proof':False,'gates':['Mode-sync child routines newly explicit','1 terminal callback body, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
