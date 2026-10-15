#!/usr/bin/env python3
"""Native/C Apollo temporary-session timer bind and logging."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-bind-temp-timer-round957';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'td_bind_temp_session_timer.c';state=sd/'td_state.c'
obj=out/'td_bind_temp_session_timer.o'
base=root/'build/c-firmware/terminal-refresh-list-round956/apollo-main-terminal-refresh-list.o'
linked=out/'apollo-main-td-bind-temp-timer.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5978ee-0x438000:0x5979b2-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t *audio_td_current_record(uint32_t s){(void)s;return (uint8_t*)0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_bind_temp_session_response_timer',str(src),str(state),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'record':'audio_td_current_record','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'record':0x597188,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,enabled,timer,session,found,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  state_addr=syms['audio_td_state'] if compiled else 0x2010fd20
  uc.mem_write(state_addr+0xa1da,bytes([enabled]))
  uc.mem_write(state_addr+0x956c,timer.to_bytes(4,'little'))
  uc.mem_write(state_addr+0x95f4,(0x98765432).to_bytes(4,'little'))
  uc.mem_write(state_addr+0x95fc+0x88,(0x11111111).to_bytes(4,'little'))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='record':calls.append((name,r0));cpu.reg_write(A.UC_ARM_REG_R0,state_addr+0x95fc if found else 0)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),string(word(sp+4)),word(sp+8)))
   else:calls.append((name,r0,string(r1),string(r2),r3));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,session),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_td_bind_temp_session_response_timer'] if compiled else 0x5978ee)|1),0x600000,count=300)
  return (uc.reg_read(A.UC_ARM_REG_R0),int.from_bytes(uc.mem_read(state_addr+0x95fc+0x88,4),'little'),tuple(calls))
 cases=[]
 for enabled in (0,1):
  for timer in (0,0xffffffff):
   for session in (0,0x1000,0xffffffff):
    for found in (False,True):
     for flags in (0,1,2,4,7):
      args=(enabled,timer,session,found,flags)
      n=run(False,*args);c=run(True,*args)
      assert n==c,(args,n,c)
      cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_bind_temp_session_response_timer'}
assert after-before=={'audio_td_current_record'}
receipt={'round':957,'status':'PASS_NATIVE_TD_BIND_TEMP_TIMER','component':'Apollo temporary-session timer bind 0x5978ee','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C gate, record child, timer field write, log call order and result','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Current-record lookup 0x597188 and list-item logger 0x5e9b84 remain open','3 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
