#!/usr/bin/env python3
"""Native/compiled-C system-alert registry callback and state effect."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-system-alert-round892';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_callback_4d2bce.c'
obj=out/'registry_callback_4d2bce.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cell=syms['audio_system_alert_message_notify']
 assert cell['st_size']==4 and elf.get_section(cell['st_shndx'])['sh_type']=='SHT_NOBITS'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x4d2bce-0x438000:0x4d2c42-0x438000]
assert native[:2].hex()=='3eb5' and native[-2:].hex()=='3ebd'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert word(0x4d3430)==0x200749f4
start,length=word(0x75d3d0),word(0x75d3cc)
assert start<=0x200749f4 and 0x200749f8<=start+length
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t audio_log_wake_allowed(void){return 0;}
uint32_t audio_system_alert_command_45a8ee(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_4d2bce',
                 str(src),str(shim),'-o',str(elf)],check=True)
 symbols={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
          if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,role,wake,flags,byte):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  state=symbols['audio_system_alert_message_notify'] if compiled else 0x200749f4
  uc.mem_write(state,b'\xa5'*4)
  uc.mem_write(0x20076000,bytes([byte]))
  native_addrs={'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e,
                'role':0x45a568,'wake':0x443484,'command':0x45a8ee}
  names={'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output','role':'audio_uart_device_role_get',
         'wake':'audio_log_wake_allowed','command':'audio_system_alert_command_45a8ee'}
  cuts={((symbols[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='role':cpu.reg_write(A.UC_ARM_REG_R0,role)
   elif op=='wake':cpu.reg_write(A.UC_ARM_REG_R0,wake)
   elif op=='command':calls.append(('command',r0,r1,r2,r3))
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),vals[2]))
   elif op=='compact':calls.append(('compact',r0,string(r1),string(r2),r3))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x11223344),(A.UC_ARM_REG_R1,0x20076000),
                  (A.UC_ARM_REG_R2,0x12345),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((symbols['audio_uart_registry_callback_4d2bce'] if compiled else 0x4d2bce)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(state,4))
 cases=[]
 for role,wake,flags,byte in ((1,1,0,0),(1,1,7,0x9a),(1,0,2,0xff),
                              (2,1,4,0x55),(0,1,1,0x80),(1,2,7,0x01)):
  n=run(False,role,wake,flags,byte);c=run(True,role,wake,flags,byte)
  assert n==c,(role,wake,flags,byte,n,c)
  cases.append({'role':role,'wake':wake,'flags':flags,'byte':byte,'calls':len(n[0])})

base=root/'build/c-firmware/quicklist-mutex-round891/apollo-main-quicklist-mutex.o'
linked=out/'apollo-main-registry-system-alert.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_registry_callback_4d2bce'}
assert after-before=={'audio_system_alert_command_45a8ee'}
receipt={'round':892,'status':'PASS_NATIVE_REGISTRY_SYSTEM_ALERT_CALLBACK',
         'component':'Apollo system-alert common-data callback',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'native_state_address':'0x200749f4','native_startup_zero_range':[hex(start),hex(start+length)],
         'cases':cases,'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'registry_callback_bodies_complete':12,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Command helper 0x45a8ee and 52 registry callback bodies remain open',
                  'Final RAM placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_REGISTRY_SYSTEM_ALERT_CALLBACK',len(cases),len(after))
