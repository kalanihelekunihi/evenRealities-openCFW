#!/usr/bin/env python3
"""Native/compiled-C protobuf ring event encoder and BLE submit traces."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-command-dispatch-round899';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_command_dispatch_5ce4e6.c'
obj=out/'ring_command_dispatch_5ce4e6.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ce4e6-0x438000:0x5ce690-0x438000]
assert hashlib.sha256(native).hexdigest()=='c50bfc78dcb2a0925d27509bf7b122ce1a0e5ce8c749e77a331578fda85d93eb'
for literal,target in ((0x5ce798,0x2037c8a0),(0x5ce79c,0x200f86fc),(0x5ce750,0x77b104)):
 assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')==target
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_ring_tx_buffer[256];
struct audio_ring_buffers_layout {uint8_t decode[64];uint8_t encode[64];};
struct audio_ring_buffers_layout audio_ring_buffers;
struct pb_msgdesc_candidate {uint32_t words[6];};
const struct pb_msgdesc_candidate audio_ring_pb_descriptor={{0}};
void audio_ring_pb_assert_509b48(void *a){(void)a;}
void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
void audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ring_command_dispatch_5ce4e6',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,has_event,size,encode_ok,flags,error):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x110000);uc.mem_map(0x20300000,0x100000)
  fixture=bytearray(20);fixture[0:2]=size.to_bytes(2,'little');fixture[2:8]=b'ABCDEF'
  fixture[8]=0x77;fixture[12:16]=b'\x78\x56\x34\x12'
  uc.mem_write(0x20076000,bytes(fixture))
  tx=syms['audio_ring_tx_buffer'] if compiled else 0x2037c8a0
  output=syms['audio_ring_buffers']+64 if compiled else 0x200f86fc
  descriptor=syms['audio_ring_pb_descriptor'] if compiled else 0x77b104
  uc.mem_write(tx,b'\xa5'*256);uc.mem_write(output,b'\xa5'*64)
  native_addrs={'assert':0x509b48,'ostream':0x4905f4,'copy':0x439c04,
                'zero':0x43c0e4,'bytes':0x439be4,'encode':0x490c32,
                'send':0x475b14,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'assert':'audio_ring_pb_assert_509b48','ostream':'audio_pb_ostream_from_buffer',
         'copy':'audio_uart_checksum_copy','zero':'audio_uart_buffer_zero',
         'bytes':'audio_queue_copy_bytes','encode':'audio_pb_encode',
         'send':'audio_ring_pb_tx_ble_475b14','flags':'audio_log_flags',
         'extended':'audio_log_extended','compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,140)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,insn_size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='assert':
    raw=bytes(cpu.mem_read(r0,20))
    p=int.from_bytes(raw[8:12],'little');f=int.from_bytes(raw[12:16],'little')
    calls.append(('assert',int.from_bytes(raw[:4],'little'),
                  int.from_bytes(raw[4:8],'little'),string(p),string(f),
                  int.from_bytes(raw[16:20],'little')))
   elif op=='ostream':
    calls.append(('ostream',r1==tx,r2))
    cpu.mem_write(r0,(0x12345679).to_bytes(4,'little')+r1.to_bytes(4,'little')+
                      r2.to_bytes(4,'little')+b'\0'*8)
   elif op=='copy':calls.append(('copy',r2));cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
   elif op=='zero':calls.append(('zero',r0==output,r1,r2));cpu.mem_write(r0,bytes([r2&255])*r1)
   elif op=='bytes':
    calls.append(('bytes',r0-output,r1-0x20076000,r2))
    cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)));cpu.reg_write(A.UC_ARM_REG_R0,r0)
   elif op=='encode':
    assert r1==descriptor and r2==output,(compiled,hex(r1),hex(descriptor),hex(r2),hex(output))
    calls.append(('encode',))
    cpu.mem_write(r0+12,(0x12345).to_bytes(4,'little'))
    if error:cpu.mem_write(r0+16,(0x78df5c).to_bytes(4,'little'))
    cpu.reg_write(A.UC_ARM_REG_R0,encode_ok)
   elif op=='send':calls.append(('send',r0,r1,r2==tx,r3))
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    vals=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    extra=(string(vals[2]),) if vals[0]==0xa0 else (vals[2],) if vals[0]==0x9d else ()
    calls.append(('extended',r0,string(r1),string(r2),string(r3),vals[0],string(vals[1]),*extra))
   elif op=='compact':
    extra=(string(r3),) if r0==0x04400000 else (r3,) if r0==0x10400000 else ()
    calls.append(('compact',r0,string(r1),string(r2),*extra))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x142),(A.UC_ARM_REG_R1,0x20076000 if has_event else 0),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_ring_command_dispatch_5ce4e6'] if compiled else 0x5ce4e6)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(output,64))
 cases=[]
 for has_event,size,encode_ok,flags,error in (
   (False,0,0,0,False),(False,0,0,7,False),
   (True,0,1,0,False),(True,3,1,7,False),(True,7,1,7,False),
   (True,3,0,0,False),(True,3,0,7,False),(True,3,0,7,True)):
  n=run(False,has_event,size,encode_ok,flags,error)
  c=run(True,has_event,size,encode_ok,flags,error)
  assert n==c,(has_event,size,encode_ok,flags,error,n,c)
  cases.append({'event':has_event,'size':size,'encode':encode_ok,'flags':flags,
                'error':error,'return':n[1],'calls':len(n[0])})

base=root/'build/c-firmware/fault-code-table-round898/apollo-main-fault-code-table.o'
linked=out/'apollo-main-ring-command-dispatch.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_ring_command_dispatch_5ce4e6'}
assert after-before=={'audio_ring_tx_buffer','audio_ring_pb_tx_ble_475b14'}
receipt={'round':899,'status':'PASS_NATIVE_RING_COMMAND_DISPATCH',
         'component':'Apollo protobuf ring event encoder and BLE submit',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_imports':sorted(after-before),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Ring transmit buffer, encode buffer, BLE send child and fault handler remain open',
                  '51 registry callbacks, final placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_RING_COMMAND_DISPATCH',len(cases),len(after))
