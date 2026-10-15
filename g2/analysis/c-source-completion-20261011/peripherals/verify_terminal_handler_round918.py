#!/usr/bin/env python3
"""Native/C session-ID-change handler comparison with source-owned tick state."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-handler-round918';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e9f74.c'
obj=out/'terminal_command_5e9f74.o'
base=root/'build/c-firmware/td-notify-state-round917/apollo-main-td-notify-state.o'
linked=out/'apollo-main-terminal-handler.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e9f74-0x438000:0x5ea000-0x438000]
assert hashlib.sha256(native).hexdigest()=='f0a83d7457023b1a597791369af1aaa314908c30fc4c8ce4fa6a519875126c64'
assert int.from_bytes(blob[0x5ea01c-0x438000:0x5ea020-0x438000],'little')+0x29c==0x2006e36c
for literal,expected in {0x5ea1e8:b'block input during session switch content sync: session=%lu tick=%lu',0x5ea1ec:b'terminal_action_session_id_changed',0x5ea1f8:b'[terminal.pb]block input during session switch content sync: session=%lu tick=%lu'}.items():
 target=int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')
 assert blob[target-0x438000:].split(b'\0')[0]==expected
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t g2_flashdb_candidate_tick(void){return 0;}
void audio_terminal_apply_session_id_changed(uint32_t a,uint8_t b){(void)a;(void)b;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e9f74',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native_hooks={0x4490cc:'tick',0x5e8346:'apply',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compact'}
 compiled_hooks={syms['g2_flashdb_candidate_tick']&~1:'tick',syms['audio_terminal_apply_session_id_changed']&~1:'apply',syms['audio_log_flags']&~1:'flags',syms['audio_log_extended']&~1:'extended',syms['compressed_log_output']&~1:'compact'}
 def run(compiled,present,session,tick,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  state=syms['audio_terminal_session_switch_tick'] if compiled else 0x2006e36c
  uc.mem_write(state,(0xfeedface).to_bytes(4,'little'))
  uc.mem_write(0x20078000,session.to_bytes(4,'little'))
  calls=[];hooks=compiled_hooks if compiled else native_hooks
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,180)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name=='tick':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,tick)
   elif name=='apply':calls.append((name,r0,r1))
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),string(word(sp+4)),word(sp+8),word(sp+12)))
   else:
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append((name,r0,string(r1),string(r2),r3,word(sp)))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x20078000 if present else 0),(A.UC_ARM_REG_R1,0x1234),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e9f74'] if compiled else 0x5e9f74)|1),0x600000,count=500)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),word(state)
 cases=[]
 for present,session,tick,flags in [(False,0,0,0)]+[(True,s,t,f) for s in (0,1,0x12345678) for t in (0,7,0xffffffff) for f in range(8)]:
  n=run(False,present,session,tick,flags);c=run(True,present,session,tick,flags)
  assert n==c,(present,session,tick,flags,n,c)
  cases.append((present,session,tick,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e9f74'}
assert after-before=={'audio_terminal_apply_session_id_changed'}
receipt={'round':918,'status':'PASS_NATIVE_TERMINAL_SESSION_ID_CHANGED','component':'Apollo terminal session-ID-change handler 0x5e9f74','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'native_ram':'0x2006e36c','cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'terminal_handlers_compiled':4,'terminal_handlers_total':12,'whole_image_complete':False,'hardware_proof':False,'gates':['terminal_apply_session_id_changed 0x5e8346 remains unresolved','Final RAM linker placement and state initialization remain unverified','8 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
