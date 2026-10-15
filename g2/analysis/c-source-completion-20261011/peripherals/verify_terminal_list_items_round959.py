#!/usr/bin/env python3
"""Native/C Apollo terminal session-list item logging contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-list-items-round959';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_log_session_list_items.c'
obj=out/'terminal_log_session_list_items.o'
base=root/'build/c-firmware/td-current-record-round958/apollo-main-td-current-record.o'
linked=out/'apollo-main-terminal-list-items.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e9b84-0x438000:0x5e9c54-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
const char *audio_terminal_session_status_name(uint32_t x){(void)x;return "STATUS";}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_log_session_list_items',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'status':'audio_terminal_session_status_name','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'status':0x5e82a4,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 payload_addr=0x20010000;status_text=0x2001f000
 def run(compiled,present,count,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  p=bytearray(0x700);p[8:10]=count.to_bytes(2,'little')
  for i in range(10):
   row=i*0x88;p[row+0xc:row+0x10]=(0x2000+i).to_bytes(4,'little')
   p[row+0x12:row+0x12+9]=f'item{i}'.encode()+b'\0\0\0\0'
   p[row+0x92]=i%4
  uc.mem_write(payload_addr,bytes(p));uc.mem_write(status_text,b'STATUS\0')
  hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
  calls=[]
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  def string(p):return bytes(uc.mem_read(p,180)).split(b'\0')[0].decode('ascii')
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='status':calls.append((name,r0&255));cpu.reg_write(A.UC_ARM_REG_R0,status_text)
   elif name=='flags':calls.append((name,));cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif name=='extended':calls.append((name,r0,string(r1),string(r2),string(r3),word(sp),string(word(sp+4)),word(sp+8),word(sp+12),word(sp+16),string(word(sp+20)),string(word(sp+24))))
   else:calls.append((name,r0,string(r1),string(r2),r3,word(sp),word(sp+4),string(word(sp+8)),string(word(sp+12))));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,payload_addr if present else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_log_session_list_items'] if compiled else 0x5e9b84)|1),0x600000,count=3000)
  return tuple(calls)
 cases=[]
 for present in (False,True):
  for count in (0,1,2,10,11):
   for flags in (0,1,2,4,7):
    args=(present,count,flags)
    n=run(False,*args);c=run(True,*args)
    assert n==c,(args,n,c)
    cases.append(args)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_log_session_list_items'} and not after-before
receipt={'round':959,'status':'PASS_NATIVE_TERMINAL_LIST_ITEMS','component':'Apollo terminal_log_session_list_items 0x5e9b84','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C ten-record clamp, status-name child, log call order and five item fields','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['3 terminal callback bodies, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
