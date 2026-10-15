#!/usr/bin/env python3
"""Native/C Apollo terminal query callback call and log contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-query-round950';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e9900.c'
obj=out/'terminal_command_5e9900.o'
base=root/'build/c-firmware/td-find-record-index-round949/apollo-main-td-find-record-index.o'
linked=out/'apollo-main-terminal-query.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e9900-0x438000:0x5e9aac-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_terminal_display_queue_handle;
uint8_t audio_terminal_ui_mode;
uint32_t audio_terminal_message_session_matches(uint32_t a,const char*b){(void)a;(void)b;return 0;}
uint32_t audio_td_session_struct_copy_out(const void*a){(void)a;return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e9900',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'match':'audio_terminal_message_session_matches','copy':'audio_td_session_struct_copy_out','display':'audio_terminal_request_display','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'match':0x5e818a,'copy':0x597be4,'display':0x5e43d2,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 payload_addr=0x20010000
 def run(compiled,present,queue,mode,match,flags,count):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  p=bytearray(0x1000)
  p[:4]=(0x1234).to_bytes(4,'little');p[6:15]=b'question\0'
  p[0x406:0x408]=count.to_bytes(2,'little')
  for i in range(3):
   pos=i*0x88;p[pos+0x408:pos+0x40c]=(0x3000+i).to_bytes(4,'little')
   p[pos+0x40e:pos+0x40e+8]=f'opt{i}'.encode()+b'\0\0\0\0'
  p[0x848:0x84c]=(0x5678).to_bytes(4,'little')
  uc.mem_write(payload_addr,bytes(p))
  uc.mem_write(syms['audio_terminal_display_queue_handle'] if compiled else 0x20074a90,queue.to_bytes(4,'little'))
  uc.mem_write(syms['audio_terminal_ui_mode'] if compiled else 0x2006e345,bytes([mode]))
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(ptr):return int.from_bytes(uc.mem_read(ptr,4),'little')
  def string(ptr):return bytes(uc.mem_read(ptr,200)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='match':calls.append((name,r0,string(r1)));cpu.reg_write(A.UC_ARM_REG_R0,match)
   elif name=='copy':calls.append((name,r0-payload_addr));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='display':calls.append((name,r0&255,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':
    fmt=string(word(sp+4));line=word(sp)
    if line==628:args=(word(sp+8),word(sp+12),word(sp+16))
    elif line==636:args=(word(sp+8),string(word(sp+12)))
    else:args=(word(sp+8),word(sp+12),string(word(sp+16)))
    calls.append((name,r0,string(r1),string(r2),string(r3),line,fmt,args))
   else:
    fmt=string(r1)
    if 'outside main' in fmt:args=(r3,word(sp),word(sp+4))
    elif 'query id' in fmt:args=(r3,string(word(sp)))
    else:args=(r3,word(sp),string(word(sp+4)))
    calls.append((name,r0,fmt,string(r2),args));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload_addr if present else 0),(A.UC_ARM_REG_R1,0xaaaa),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_5e9900'] if compiled else 0x5e9900)|1),0x600000,count=1500)
  return (uc.reg_read(A.UC_ARM_REG_R0),tuple(calls))
 cases=[]
 for present in (False,True):
  for queue in (0,0x1234):
   for mode in (0,7):
    for match in (0,1):
     for flags in (0,1,2,4,7):
      for count in (0,1,2):
       args=(present,queue,mode,match,flags,count)
       n=run(False,*args);c=run(True,*args)
       assert n==c,(args,n,c)
       cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e9900'}
assert after-before=={'audio_terminal_message_session_matches','audio_td_session_struct_copy_out'}
receipt={'round':950,'status':'PASS_NATIVE_TERMINAL_QUERY','component':'Apollo terminal_action_query 0x5e9900','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C gate, child/log call order, option records, return code','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Session match 0x5e818a and copy-out 0x597be4 remain open','4 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
