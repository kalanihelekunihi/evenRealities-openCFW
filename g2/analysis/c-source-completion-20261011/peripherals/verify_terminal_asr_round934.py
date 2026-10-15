#!/usr/bin/env python3
"""Native/C ASR-result terminal callback branch and dependency differential."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-asr-round934';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e8e6c.c'
obj=out/'terminal_command_5e8e6c.o'
base=root/'build/c-firmware/terminal-apply-session-round933/apollo-main-terminal-apply-session.o'
linked=out/'apollo-main-terminal-asr.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e8e6c-0x438000:0x5e9026-0x438000]
assert hashlib.sha256(native).hexdigest()=='22b6d8a50dd2500ca72f088ac3d494176f9f25ffe8426d5dd3604c3df638758e'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
uint32_t audio_td_ring_write(const void *a){(void)a;return 0;}
const uint8_t *audio_td_state_ptr(void){return 0;}
void audio_td_notify_state_clear(void){}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e8e6c',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'ring':'audio_td_ring_write','state':'audio_td_state_ptr','notify':'audio_td_notify_state_clear','display':'audio_terminal_request_display','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'ring':0x5976d8,'state':0x597318,'notify':0x597110,'display':0x5e43d2,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,present,all_final,sentence_final,mode,have_state,cached,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  payload=0x20076000
  data=bytearray(0x204);data[0:2]=(5).to_bytes(2,'little');data[2:8]=b'HELLO\0';data[0x202]=sentence_final;data[0x203]=all_final
  uc.mem_write(payload,bytes(data))
  uc.mem_write(0x20078000+0x802,(3 if cached else 0).to_bytes(2,'little'))
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
   if name=='ring':calls.append((name,r0))
   elif name=='state':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,0x20078000 if have_state else 0)
   elif name=='notify':calls.append((name,))
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0x77)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(word(sp+4))
    if 'len:' in msg:args=(word(sp+8),word(sp+12),word(sp+16))
    elif msg=='%s':args=(string(word(sp+8)),)
    else:args=()
    calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),msg,args))
   else:
    sp=cpu.reg_read(A.UC_ARM_REG_SP);msg=string(r1)
    if 'len:' in msg:args=(r3,word(sp),word(sp+4))
    elif msg=='[terminal.pb]%s':args=(string(r3),)
    else:args=()
    calls.append((name,r0,msg,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0x66)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload if present else 0),(A.UC_ARM_REG_R1,0x1234),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e8e6c'] if compiled else 0x5e8e6c)|1),0x600000,count=1000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for present,all_final,sentence_final,mode,have_state,cached,flags in [(False,0,0,0,0,0,0)]+[(True,a,s,m,h,c,f) for a in (0,1) for s in (0,1) for m in (0,4) for h in (0,1) for c in (0,1) for f in range(8)]:
  n=run(False,present,all_final,sentence_final,mode,have_state,cached,flags)
  c=run(True,present,all_final,sentence_final,mode,have_state,cached,flags)
  assert n==c,(present,all_final,sentence_final,mode,have_state,cached,flags,n,c)
  cases.append((present,all_final,sentence_final,mode,have_state,cached,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e8e6c'}
assert after-before=={'audio_td_ring_write','audio_td_state_ptr'}
receipt={'round':934,'status':'PASS_NATIVE_TERMINAL_ASR_RESULT','component':'Apollo terminal_action_asr_result 0x5e8e6c','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C child and logging call-order differential','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'terminal_handlers_compiled':6,'terminal_handlers_total':12,'whole_image_complete':False,'hardware_proof':False,'gates':['td_ring_write 0x5976d8 and td_state_ptr 0x597318 remain open','6 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
