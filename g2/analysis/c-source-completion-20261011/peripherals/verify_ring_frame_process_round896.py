#!/usr/bin/env python3
"""Native/compiled-C RingDataRelay frame processor branch traces."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-frame-process-round896';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_frame_process_5ce1dc.c'
obj=out/'ring_frame_process_5ce1dc.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ce1dc-0x438000:0x5ce3ce-0x438000]
assert hashlib.sha256(native).hexdigest()=='91584b2a82140bf9e7a99283d76e3ceef267daeb75d469caf283037b3c9e2ed6'
assert int.from_bytes(blob[0x5ce74c-0x438000:0x5ce750-0x438000],'little')==0x200f86bc
assert int.from_bytes(blob[0x5ce750-0x438000:0x5ce754-0x438000],'little')==0x77b104
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
struct audio_ring_buffers_layout {uint8_t decode[64];uint8_t encode[64];};
struct audio_ring_buffers_layout audio_ring_buffers;
struct pb_msgdesc_candidate {uint32_t words[6];};
const struct pb_msgdesc_candidate audio_ring_pb_descriptor={{0}};
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_pb_stream_init(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_pb_decode(void*a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_ring_command_validate_5ce3ce(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_ring_command_dispatch_5ce4e6(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ring_data_relay_5ce1dc',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,has_data,decode_ok,command,validate,flags,error):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x110000)
  uc.mem_write(0x20076000,b'abcdefgh')
  decoded=syms['audio_ring_buffers'] if compiled else 0x200f86bc
  descriptor=syms['audio_ring_pb_descriptor'] if compiled else 0x77b104
  uc.mem_write(decoded,b'\xa5'*64)
  native_addrs={'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e,
                'zero':0x43c0e4,'init':0x48f49c,'copy':0x439c04,'decode':0x490120,
                'validate':0x5ce3ce,'dispatch':0x5ce4e6}
  names={'flags':'audio_log_flags','extended':'audio_log_extended',
         'compact':'compressed_log_output','zero':'audio_uart_buffer_zero',
         'init':'audio_uart_pb_stream_init','copy':'audio_uart_checksum_copy',
         'decode':'audio_uart_pb_decode','validate':'audio_ring_command_validate_5ce3ce',
         'dispatch':'audio_ring_command_dispatch_5ce4e6'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,140)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='zero':calls.append(('zero',r0==decoded,r1,r2));cpu.mem_write(r0,bytes([r2&255])*r1)
   elif op=='init':
    calls.append(('init',r1,r2))
    cpu.mem_write(r0,(0x12345678).to_bytes(4,'little')+r1.to_bytes(4,'little')+
                      r2.to_bytes(4,'little')+b'\0'*4)
   elif op=='copy':
    calls.append(('copy',r2));cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
   elif op=='decode':
    assert r1==descriptor and r2==decoded,(compiled,hex(r1),hex(descriptor),hex(r2),hex(decoded))
    calls.append(('decode',))
    cpu.mem_write(decoded,bytes([command,0x42]))
    if error:cpu.mem_write(r0+12,(0x78df5c).to_bytes(4,'little'))
    cpu.reg_write(A.UC_ARM_REG_R0,decode_ok)
   elif op in ('validate','dispatch'):
    calls.append((op,r0,r1-decoded))
    cpu.reg_write(A.UC_ARM_REG_R0,validate if op=='validate' else 0x7b)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    extra=(string(vals[2]),) if vals[0]==0x3d else (vals[2],) if vals[0] in (0x31,0x41,0x4e) else ()
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),*extra))
   elif op=='compact':
    extra=(string(r3),) if r0==0x04400000 else (r3,) if r0 in (0x10400000,0x08400000) else ()
    calls.append(('compact',r0,string(r1),string(r2),*extra))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x20076000 if has_data else 0),
                  (A.UC_ARM_REG_R1,8),(A.UC_ARM_REG_SP,0x200ff000),
                  (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_ring_data_relay_5ce1dc'] if compiled else 0x5ce1dc)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(decoded,64))
 cases=[]
 for has_data,decode_ok,command,validate,flags,error in (
   (False,0,0,0,0,False),(False,0,0,0,7,False),
   (True,0,0,0,0,False),(True,0,0,0,7,False),(True,0,0,0,7,True),
   (True,1,1,0,0,False),(True,1,1,0,7,False),(True,1,1,2,7,False),
   (True,1,2,0,7,False)):
  n=run(False,has_data,decode_ok,command,validate,flags,error)
  c=run(True,has_data,decode_ok,command,validate,flags,error)
  assert n==c,(has_data,decode_ok,command,validate,flags,error,n,c)
  cases.append({'data':has_data,'decode':decode_ok,'command':command,
                'validate':validate,'flags':flags,'error':error,'return':n[1]})

base=root/'build/c-firmware/registry-ring-data-round895/apollo-main-registry-ring-data.o'
linked=out/'apollo-main-ring-frame-process.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_ring_data_relay_5ce1dc'}
assert after-before=={'audio_ring_buffers','audio_ring_pb_descriptor',
                      'audio_ring_command_validate_5ce3ce','audio_ring_command_dispatch_5ce4e6'}
receipt={'round':896,'status':'PASS_NATIVE_RING_FRAME_PROCESSOR',
         'component':'Apollo RingDataRelay frame processor',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_imports':sorted(after-before),
         'registry_callback_bodies_complete':13,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Ring protobuf descriptor/buffer ownership and two command children remain open',
                  '51 registry callbacks, final placement, and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_RING_FRAME_PROCESSOR',len(cases),len(after))
