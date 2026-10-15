#!/usr/bin/env python3
"""Native/C terminal dispatcher comparison across all byte event IDs."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-command-route-round912';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_route_5ea028.c'
table=root/'components/audio/uart_thread_source_candidate/terminal_command_handlers_72eb78.c'
obj=out/'terminal_command_route_5ea028.o'
base=root/'build/c-firmware/terminal-command-table-round911/apollo-main-terminal-command-table.o'
linked=out/'apollo-main-terminal-command-route.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ea028-0x438000:0x5ea152-0x438000]
targets=struct.unpack_from('<13I',blob,0x72eb78-0x438000)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 children='\n'.join(f'uint32_t audio_terminal_command_{(v&~1):x}(const void*a,uint32_t b){{(void)a;(void)b;return 0;}}'
                    for v in targets[1:])
 shim.write_text('''#include <stdint.h>
const char *audio_terminal_event_name_5ea004(uint32_t a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
'''+children+'\n')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_route_5ea028',
                 str(src),str(table),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'name':'audio_terminal_event_name_5ea004','flags':'audio_log_flags',
        'extended':'audio_log_extended','compact':'compressed_log_output'}
 native_addrs={'name':0x5ea004,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
 def run(compiled,event,flags_value):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  uc.mem_write(0x20078000,b'EVENT\0')
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items()}
  for i,target in enumerate(targets[1:],1):
   hooks[((syms[f'audio_terminal_command_{(target&~1):x}'] if compiled else target)&~1)]=f'child{i}'
  def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def word(p):return int.from_bytes(uc.mem_read(p,4),'little')
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   if name=='name':
    calls.append(('name',r0));cpu.reg_write(A.UC_ARM_REG_R0,0x20078000)
   elif name=='flags':
    calls.append(('flags',));cpu.reg_write(A.UC_ARM_REG_R0,flags_value)
   elif name=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append(('extended',r0,string(r1),string(r2),string(r3),word(sp),
                  string(word(sp+4)),word(sp+8),string(word(sp+12)) if event%256<13 else None))
   elif name=='compact':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append(('compact',r0,string(r1),string(r2),r3,
                  string(word(sp)) if event%256<13 else None))
   else:
    calls.append((name,r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,0x77)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,0x20076000),
                  (A.UC_ARM_REG_R2,0x12345),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_terminal_command_route_5ea028'] if compiled else 0x5ea028)|1),
               0x600000,count=1000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for event,flags_value in [(i,0) for i in range(256)]+[(0,7),(1,7),(12,7),(13,7),(0x101,7)]:
  n=run(False,event,flags_value);c=run(True,event,flags_value)
  assert n==c,(event,flags_value,n,c)
  cases.append({'event':event,'flags':flags_value,'calls':len(n[0]),'return':n[1]})
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_route_5ea028'}
assert after-before=={'audio_terminal_event_name_5ea004'}
receipt={'round':912,'status':'PASS_NATIVE_TERMINAL_COMMAND_ROUTE',
 'component':'Apollo terminal_machine_handler 0x5ea028',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'all_event_bytes':True,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Runtime event-name array and helper 0x5ea004 remain open',
          'Twelve route child bodies, ring-connect parse buffer, 49 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
