#!/usr/bin/env python3
"""Native/compiled-C Thread_MsgPbTxByBle gate and BLE ABI."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-pb-tx-ble-round900';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_pb_tx_ble_475b14.c'
obj=out/'ring_pb_tx_ble_475b14.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x475b14-0x438000:0x475c1a-0x438000]
assert hashlib.sha256(native).hexdigest()=='6ea569a77990f9df338832a3e582b6485be6b1252d5973c257fc603e1f475891'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint32_t audio_ota_transfer_active(void){return 0;}
uint32_t audio_app_is_left_slave_role(void){return 0;}
uint32_t audio_ble_msg_tx(uint8_t a,uint8_t b,uint8_t c,uint8_t d,const void*e,uint16_t f)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ring_pb_tx_ble_475b14',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,ota,left,flags):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x100000)
  native_addrs={'ota':0x4487ac,'left':0x46f258,'tx':0x47564e,
                'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  names={'ota':'audio_ota_transfer_active','left':'audio_app_is_left_slave_role',
         'tx':'audio_ble_msg_tx','flags':'audio_log_flags',
         'extended':'audio_log_extended','compact':'compressed_log_output'}
  cuts={((syms[v]&~1) if compiled else native_addrs[k]):k for k,v in names.items()}
  calls=[]
  def string(ptr):return bytes(uc.mem_read(ptr,120)).split(b'\0')[0].decode('ascii')
  def hook(cpu,addr,size,user):
   op=cuts.get(addr)
   if op is None:return
   r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if op=='ota':calls.append(('ota',));cpu.reg_write(A.UC_ARM_REG_R0,ota)
   elif op=='left':calls.append(('left',));cpu.reg_write(A.UC_ARM_REG_R0,left)
   elif op=='tx':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    payload=int.from_bytes(cpu.mem_read(sp,4),'little')
    length=int.from_bytes(cpu.mem_read(sp+4,4),'little')
    calls.append(('tx',r0,r1,r2,r3,payload,length))
    cpu.reg_write(A.UC_ARM_REG_R0,0x1234)
   elif op=='flags':cpu.reg_write(A.UC_ARM_REG_R0,flags)
   elif op=='extended':
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    line=int.from_bytes(cpu.mem_read(sp,4),'little')
    msg=int.from_bytes(cpu.mem_read(sp+4,4),'little')
    calls.append(('extended',r0,string(r1),string(r2),string(r3),line,string(msg)))
   elif op=='compact':calls.append(('compact',r0,string(r1),string(r2)))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((A.UC_ARM_REG_R0,0x123),(A.UC_ARM_REG_R1,0x145),
                  (A.UC_ARM_REG_R2,0x20076000),(A.UC_ARM_REG_R3,0x12345),
                  (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
   uc.reg_write(reg,val)
  uc.emu_start(((syms['audio_ring_pb_tx_ble_475b14'] if compiled else 0x475b14)|1),
               0x600000,count=10000)
  return calls,uc.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for ota,left,flags in ((1,0,0),(1,0,7),(0,1,0),(0,1,7),(0,0,0),(0,0,7)):
  n=run(False,ota,left,flags);c=run(True,ota,left,flags)
  assert n==c,(ota,left,flags,n,c)
  cases.append({'ota':ota,'left':left,'flags':flags,'return':n[1],'calls':len(n[0])})

base=root/'build/c-firmware/ring-command-dispatch-round899/apollo-main-ring-command-dispatch.o'
linked=out/'apollo-main-ring-pb-tx-ble.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_ring_pb_tx_ble_475b14'} and not after-before
receipt={'round':900,'status':'PASS_NATIVE_RING_PB_TX_BLE',
         'component':'Apollo ring protobuf BLE transport gate',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':cases,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Ring buffer placement and fault handler remain open',
                  '51 registry callbacks, final placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_RING_PB_TX_BLE',len(cases),len(after))
