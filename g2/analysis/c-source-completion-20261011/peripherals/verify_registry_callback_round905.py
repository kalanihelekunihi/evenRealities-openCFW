#!/usr/bin/env python3
"""Native/C branch and state comparison for ring-connect registry callback."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-callback-round905';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_callback_5e4488.c'
obj=out/'registry_callback_5e4488.o'
base=root/'build/c-firmware/registry-callback-round904/apollo-main-registry-callback.o'
linked=out/'apollo-main-registry-ring-connect.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e4488-0x438000:0x5e44f6-0x438000]
assert int.from_bytes(blob[0x5e4794-0x438000:0x5e4798-0x438000],'little')==0x2010f4cc
assert int.from_bytes(blob[0x5e4798-0x438000:0x5e479c-0x438000],'little')==0x2010fd1c
row=struct.unpack_from('<4I',blob,0x6a46b0-0x438000)
assert row[0]==0x30 and (row[1]&~1)==0x5e4488
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_registry_ring_connect_buffer[256];
uint8_t audio_registry_ring_connect_state;
void audio_registry_ring_connect_enter_5e438e(uint32_t a){(void)a;}
uint32_t audio_registry_ring_connect_parse_5ce990(const void*a,uint16_t b,uint8_t*c)
{(void)a;(void)b;(void)c;return 0;}
uint32_t audio_registry_ring_connect_notify_5ceaec(uint8_t*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_registry_ring_connect_check_5e4604(const uint8_t*a){(void)a;return 0;}
void audio_registry_ring_connect_leave_5e43be(void){}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_5e4488',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'enter':'audio_registry_ring_connect_enter_5e438e',
        'parse':'audio_registry_ring_connect_parse_5ce990',
        'notify':'audio_registry_ring_connect_notify_5ceaec',
        'check':'audio_registry_ring_connect_check_5e4604',
        'leave':'audio_registry_ring_connect_leave_5e43be'}
 native_addrs={'enter':0x5e438e,'parse':0x5ce990,'notify':0x5ceaec,
               'check':0x5e4604,'leave':0x5e43be}
 def run(compiled,event,length,parse_status,check_status):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x120000)
  buf=syms['audio_registry_ring_connect_buffer'] if compiled else 0x2010f4cc
  state=syms['audio_registry_ring_connect_state'] if compiled else 0x2010fd1c
  uc.mem_write(buf,b'\xa5\x42'+b'\xa5'*30);uc.mem_write(state,b'\xa5')
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items()}
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2)
   if name=='enter':calls.append((name,r0))
   elif name=='parse':
    calls.append((name,r0,r1,r2==buf));cpu.reg_write(A.UC_ARM_REG_R0,parse_status)
   elif name=='check':
    calls.append((name,r0==buf));cpu.reg_write(A.UC_ARM_REG_R0,check_status)
   elif name=='notify':calls.append((name,r0==state,r1))
   else:calls.append((name,))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,0x20076000),
                  (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_uart_registry_callback_5e4488'] if compiled else 0x5e4488)|1),
               0x600000,count=1000)
  return calls,bytes(uc.mem_read(state,1)),uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for event,length,parse_status,check_status in [(1,0x12345,0,0),(0,0x12345,13,0),
                                                 (0,0x12345,2,0),(0,0,0,0),(0,0xffff,0,1)]:
  n=run(False,event,length,parse_status,check_status)
  c=run(True,event,length,parse_status,check_status)
  assert n==c,(event,length,parse_status,check_status,n,c)
  cases.append({'event':event,'length':length,'parse_status':parse_status,
                'check_status':check_status,'calls':len(n[0]),'state':n[1][0]})
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_uart_registry_callback_5e4488'}
assert after-before==set(names.values())|{'audio_registry_ring_connect_buffer','audio_registry_ring_connect_state'}
receipt={'round':905,'status':'PASS_NATIVE_REGISTRY_RING_CONNECT_CALLBACK',
 'component':'Apollo registry callback 0x5e4488',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'registry_row':hex(0x6a46b0),'cases':cases,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'registry_callback_bodies_complete':15,'registry_callback_bodies_total':64,
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Five ring-connect child bodies and two RAM state symbols remain open',
          '49 registry callback bodies, unknown fault-code behavior, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
