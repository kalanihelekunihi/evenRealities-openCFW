#!/usr/bin/env python3
"""Native/compiled-C Quicklist mutex initialization and BSS owner."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/quicklist-mutex-round891';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/quicklist_data_mutex_4ffa70.c'
obj=out/'quicklist_data_mutex_4ffa70.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 state=syms['audio_quicklist_storage_mutex']
 assert state['st_size']==4 and elf.get_section(state['st_shndx'])['sh_type']=='SHT_NOBITS'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x4ffa70-0x438000:0x4ffac8-0x438000]
assert native[:2].hex()=='1cb5' and native[-2:].hex()=='16bd'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert word(0x4ffba8)==0x200748f0
start,length=word(0x75d3d0),word(0x75d3cc)
assert start<=0x200748f0 and 0x200748f4<=start+length
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void *audio_uart_mutex_new(const void *a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_quicklist_data_mutex_init_4ffa70',
                 str(src),str(shim),'-o',str(elf)],check=True)
 symbols={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
          if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,initial,created,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  cell=symbols['audio_quicklist_storage_mutex'] if compiled else 0x200748f0
  uc.mem_write(cell,initial.to_bytes(4,'little'))
  native_addrs={'new':0x44971c,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'new':'audio_uart_mutex_new','flags':'audio_log_flags',
         'extended':'audio_log_extended','compact':'compressed_log_output'}
  cuts={((symbols[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='new':calls.append(('new',r0));cpu.reg_write(A.UC_ARM_REG_R0,created)
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    line=int.from_bytes(cpu.mem_read(sp,4),'little')
    msg=int.from_bytes(cpu.mem_read(sp+4,4),'little')
    calls.append(('extended',r0,string(r1),string(r2),string(r3),line,string(msg)))
   elif op=='compact':calls.append(('compact',r0,string(r1),string(r2)))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
  uc.emu_start(((symbols['audio_quicklist_data_mutex_init_4ffa70'] if compiled else 0x4ffa70)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),int.from_bytes(uc.mem_read(cell,4),'little')
 cases=[]
 for initial,created,flags in ((0x20070000,0,0),(0,0x20070000,0),
                               (0,0,0),(0,0,2),(0,0,4),(0,0,7)):
  n=run(False,initial,created,flags);c=run(True,initial,created,flags)
  assert n==c,(initial,created,flags,n,c)
  cases.append({'initial':initial,'created':created,'flags':flags,'return':n[1],'state':n[2]})

base=root/'build/c-firmware/registry-quicklist-round890/apollo-main-registry-quicklist.o'
linked=out/'apollo-main-quicklist-mutex.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_quicklist_data_mutex_init_4ffa70'} and not after-before
receipt={'round':891,'status':'PASS_NATIVE_QUICKLIST_MUTEX_OWNER',
         'component':'Apollo Quicklist storage mutex initialization',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'native_state_address':'0x200748f0','native_startup_zero_range':[hex(start),hex(start+length)],
         'cases':cases,'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'registry_callback_bodies_complete':11,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Three Quicklist child bodies and 53 registry callback bodies remain open',
                  'Final mutex RAM placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_QUICKLIST_MUTEX_OWNER',len(cases),len(after))
