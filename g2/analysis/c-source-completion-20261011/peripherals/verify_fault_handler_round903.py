#!/usr/bin/env python3
"""Native/C fault-handler comparison for defined table codes and type branches."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/fault-handler-round903';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/fault_handler_509b48.c'
table=root/'components/audio/uart_thread_source_candidate/fault_code_table_6c8e60.c'
obj=out/'fault_handler_509b48.o'
flags=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11',
       '-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror']
subprocess.run(['clang',*flags,'-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x509b48-0x438000:0x509bfa-0x438000]
assert hashlib.sha256(native).hexdigest()=='3c12f284fbaedb30146e40bad627cebfa6cf2a505d9e5b7fff74b13df2d9e971'
for literal,value in [(0x509bfc,0x6c8e60),(0x509c00,0x77d78c),(0x509c04,0x7746e8)]:
 assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')==value
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_ble_format_to_buffer(char*a,const char*b,...){(void)a;(void)b;return 0;}
const char *audio_fault_unmapped_code_message_509b48(uint16_t a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ring_pb_assert_509b48',
                 str(src),str(table),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,kind,detail,flags_value):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  rec=0x20076000;sp=0x200ff000
  source_path=0x20076100;source_fn=0x20076140;word=0x20076180
  uc.mem_write(source_path,b'caller.c\0');uc.mem_write(source_fn,b'caller_fn\0')
  uc.mem_write(word,b'condition\0')
  if kind==1:detail=word
  for i,v in enumerate((kind,detail,source_path,source_fn,42)):
   uc.mem_write(rec+4*i,v.to_bytes(4,'little'))
  names={'zero':'audio_uart_buffer_zero','format':'audio_ble_format_to_buffer',
         'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output','unknown':'audio_fault_unmapped_code_message_509b48'}
  native_addrs={'zero':0x43c0e4,'format':0x4b4728,'flags':0x43d0ce,
                'extended':0x43d574,'compact':0x43ce9e}
  hooks={((syms[symbol] if compiled else native_addrs[name])&~1):name
         for name,symbol in names.items() if (name!='unknown' or compiled)}
  def string(addr):
   if addr==0:return ''
   try:return bytes(uc.mem_read(addr,512)).split(b'\0')[0].decode('ascii')
   except Exception:return '<invalid>'
  def word_at(addr):return int.from_bytes(uc.mem_read(addr,4),'little')
  calls=[]
  def hook(cpu,address,size,user):
   name=hooks.get(address)
   if not name:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
   r2=cpu.reg_read(A.UC_ARM_REG_R2);r3=cpu.reg_read(A.UC_ARM_REG_R3)
   stk=cpu.reg_read(A.UC_ARM_REG_SP)
   if name=='zero':
    calls.append(('zero',r1,r2));cpu.mem_write(r0,b'\0'*r1)
   elif name=='format':
    calls.append(('format',string(r1),r2,string(r3)))
    cpu.mem_write(r0,b'formatted\0');cpu.reg_write(A.UC_ARM_REG_R0,9)
   elif name=='flags':
    calls.append(('flags',));cpu.reg_write(A.UC_ARM_REG_R0,flags_value)
   elif name=='extended':
    calls.append(('extended',r0,string(r1),string(r2),string(r3),
                  word_at(stk),string(word_at(stk+4)),string(word_at(stk+8)),
                  string(word_at(stk+12)),word_at(stk+16),string(word_at(stk+20))))
   elif name=='compact':
    calls.append(('compact',r0,string(r1),string(r2),string(r3),
                  string(word_at(stk)),word_at(stk+4),string(word_at(stk+8))))
   else:raise AssertionError('unmapped helper called in covered case')
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,rec),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start((syms['audio_ring_pb_assert_509b48'] if compiled else 0x509b48)|1,
               0x600000,count=20000)
  return calls
 cases=[]
 for kind,detail in ((0,0),(0,2),(0,0x80),(1,0),(2,0),
                     (0x100,2),(0x101,0),(0x102,0)):
  for flags_value in (0,2,1,4):
   n=run(False,kind,detail,flags_value);c=run(True,kind,detail,flags_value)
   assert n==c,(kind,detail,flags_value,n,c)
   cases.append({'kind':kind,'detail':detail,'flags':flags_value,'calls':len(n)})
base=root/'build/c-firmware/ring-pb-descriptor-round902/apollo-main-ring-pb-descriptor.o'
linked=out/'apollo-main-fault-handler.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_ring_pb_assert_509b48'}
assert after-before=={'audio_fault_unmapped_code_message_509b48'}
defined={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(linked)],text=True).splitlines()}
assert {'audio_ring_pb_assert_509b48','audio_ble_format_to_buffer','g2_iar_general_format'}<=defined
receipt={'round':903,'status':'PASS_NATIVE_FAULT_HANDLER_DEFINED_CODES',
 'component':'Apollo fault handler 0x509b48 defined-code branches',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
 'selected_formatter_symbols':['audio_ble_format_to_buffer','g2_iar_general_format'],
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Native unknown-code search past the 43-row table remains unresolved',
          '51 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
