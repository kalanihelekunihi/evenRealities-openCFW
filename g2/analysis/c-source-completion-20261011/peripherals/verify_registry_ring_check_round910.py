#!/usr/bin/env python3
"""Compare all terminal command bytes with native 0x5e4604."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-ring-check-round910';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_ring_connect_check_5e4604.c'
obj=out/'registry_ring_connect_check_5e4604.o'
base=root/'build/c-firmware/registry-ring-notify-round909/apollo-main-registry-ring-notify.o'
linked=out/'apollo-main-registry-ring-check.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e4604-0x438000:0x5e4764-0x438000]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_terminal_command_route_5ea028(uint32_t a,const void*b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_registry_ring_connect_check_5e4604',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'route':'audio_terminal_command_route_5ea028','flags':'audio_log_flags',
        'extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'route':0x5ea028,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,command,flags_value):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  ptr=0 if command is None else 0x20076000
  if ptr:uc.mem_write(ptr,bytes([command])+b'\xa5'*2200)
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items()}
  def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name=='route':
    calls.append(('route',r0,r1==ptr+4,r2));cpu.reg_write(A.UC_ARM_REG_R0,0x77)
   elif name=='flags':
    calls.append(('flags',));cpu.reg_write(A.UC_ARM_REG_R0,flags_value)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append(('extended',r0,string(r1),string(r2),string(r3),word(sp),
                  string(word(sp+4)),word(sp+8) if command!=163 else None))
   else:
    calls.append(('compact',r0,string(r1),string(r2),r3 if command!=163 else None))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,ptr),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_registry_ring_connect_check_5e4604'] if compiled else 0x5e4604)|1),
               0x600000,count=500)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for command,flags_value in [(None,0)]+[(i,0) for i in range(256)]+[(163,7),(254,7)]:
  n=run(False,command,flags_value);c=run(True,command,flags_value)
  assert n==c,(command,flags_value,n,c)
  cases.append({'command':command,'flags':flags_value,'calls':len(n[0]),'return':n[1]})
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_registry_ring_connect_check_5e4604'}
assert after-before=={'audio_terminal_command_route_5ea028'}
receipt={'round':910,'status':'PASS_NATIVE_REGISTRY_RING_COMMAND_CHECK',
 'component':'Apollo terminal command receive handler 0x5e4604',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'all_command_bytes':True,'logged_cases':[163,254],
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Command route child 0x5ea028 remains open',
          'Ring-connect parse child and buffer, terminal send child, 49 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
