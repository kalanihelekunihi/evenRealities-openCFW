#!/usr/bin/env python3
"""Native/compiled-C PB_RxRingEvent validation effects."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-command-validate-round897';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_command_validate_5ce3ce.c'
obj=out/'ring_command_validate_5ce3ce.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ce3ce-0x438000:0x5ce4e6-0x438000]
assert hashlib.sha256(native).hexdigest()=='807dda29aad8d7dd432396548b36068614a066a0a7e1c128b0e1051798080ddc'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ring_pb_assert_509b48(void *a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ring_command_validate_5ce3ce',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,has_event,size,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  fixture=bytearray(20);fixture[0:2]=b'\x34\x12';fixture[8]=size
  fixture[12:16]=b'\x78\x56\x34\x12';uc.mem_write(0x20076000,bytes(fixture))
  native_addrs={'copy':0x439c04,'assert':0x509b48,'flags':0x43d0ce,
                'extended':0x43d574,'compact':0x43ce9e}
  names={'copy':'audio_uart_checksum_copy','assert':'audio_ring_pb_assert_509b48',
         'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,160)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,insn_size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='copy':calls.append(('copy',r2));cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
   elif op=='assert':
    raw=bytes(cpu.mem_read(r0,20))
    code=int.from_bytes(raw[:4],'little');detail=int.from_bytes(raw[4:8],'little')
    p=int.from_bytes(raw[8:12],'little');f=int.from_bytes(raw[12:16],'little')
    line=int.from_bytes(raw[16:20],'little')
    calls.append(('assert',code,detail,string(p),string(f),line))
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(5)]
    extra=tuple(vals[2:5]) if vals[0]==0x5f else (vals[2],) if vals[0]==0x79 else ()
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),*extra))
   elif op=='compact':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    extra=(r3,int.from_bytes(cpu.mem_read(sp,4),'little'),
           int.from_bytes(cpu.mem_read(sp+4,4),'little')) if r0==0x0cc00000 else (r3,) if r0==0x08400000 else ()
    calls.append(('compact',r0,string(r1),string(r2),*extra))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x42),(A.UC_ARM_REG_R1,0x20076000 if has_event else 0),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_ring_command_validate_5ce3ce'] if compiled else 0x5ce3ce)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for event,size,flags in ((False,0,0),(False,0,7),(True,1,0),
                          (True,1,7),(True,2,2),(True,2,4),(True,0xff,7)):
  n=run(False,event,size,flags);c=run(True,event,size,flags)
  assert n==c,(event,size,flags,n,c)
  cases.append({'event':event,'size':size,'flags':flags,'return':n[1],'calls':len(n[0])})

base=root/'build/c-firmware/ring-frame-process-round896/apollo-main-ring-frame-process.o'
linked=out/'apollo-main-ring-command-validate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_ring_command_validate_5ce3ce'}
assert after-before=={'audio_ring_pb_assert_509b48'}
receipt={'round':897,'status':'PASS_NATIVE_RING_COMMAND_VALIDATE',
         'component':'Apollo ring event validation',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Ring fault handler 0x509b48 and dispatch child 0x5ce4e6 remain open',
                  '51 registry callbacks, final placement, and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_RING_COMMAND_VALIDATE',len(cases),len(after))
