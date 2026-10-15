#!/usr/bin/env python3
"""Native/C BLE status callback registration call and logging contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ble-status-callbacks-round987';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/display_ble_status_callbacks.c'
obj=out/'display_ble_status_callbacks.o'
base=root/'build/c-firmware/fal-partition-erase-round986/apollo-main-fal-partition-erase.o'
linked=out/'apollo-main-ble-status-callbacks.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x4abcc6-0x438000:0x4abd60-0x438000]
assert int.from_bytes(blob[0x4abd74-0x438000:0x4abd78-0x438000],'little')==0x20073f6c
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_callback_mgr_register(void*a,void*b){(void)a;(void)b;return 0;}
void audio_callback_mgr_unregister(void*a,void*b){(void)a;(void)b;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_status_register_callback',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'register':'audio_callback_mgr_register','unregister':'audio_callback_mgr_unregister','flags':'audio_log_flags','log':'audio_log_extended','short':'compressed_log_output'}
 addrs={'register':0x510240,'unregister':0x5103c4,'flags':0x43d0ce,'log':0x43d574,'short':0x43ce9e}
 cases=[]
 for action in ('register','unregister'):
  for present in (False,True):
   for flags in (0,1,2,4,7):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     manager=syms['audio_ble_status_callback_manager'] if compiled else 0x20073f6c
     uc.mem_write(manager,bytes(range(12)))
     callback=0x20010001 if present else 0
     hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in addrs.items()}
     calls=[]
     def string(p):return bytes(uc.mem_read(p,180)).split(b'\0')[0].decode('ascii')
     def hook(cpu,pc,size,user):
      kind=hooks.get(pc)
      if not kind:return
      r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
      sp=cpu.reg_read(A.UC_ARM_REG_SP)
      if kind in ('register','unregister'):calls.append((kind,r[0]-manager,r[1]-callback));ret=0x1234
      elif kind=='flags':calls.append(('flags',));ret=flags
      elif kind=='log':calls.append(('log',r[0],string(r[1]),string(r[2]),string(r[3]),int.from_bytes(cpu.mem_read(sp,4),'little'),string(int.from_bytes(cpu.mem_read(sp+4,4),'little'))));ret=0
      else:calls.append(('short',r[0],string(r[1]),string(r[2])));ret=0
      cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     uc.reg_write(A.UC_ARM_REG_R0,callback);uc.reg_write(A.UC_ARM_REG_SP,0x201ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
     entry=(syms['audio_ble_status_'+action+'_callback'] if compiled else (0x4abcc6 if action=='register' else 0x4abd14))|1
     uc.emu_start(entry,0x600000,count=150)
     outputs.append((calls,bytes(uc.mem_read(manager,12))))
    assert outputs[0]==outputs[1],(action,present,flags,outputs)
    cases.append((action,present,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_ble_status_register_callback','audio_ble_status_unregister_callback'}
assert after-before=={'audio_callback_mgr_unregister'}
receipt={'round':987,'status':'PASS_NATIVE_BLE_STATUS_CALLBACK_WRAPPERS','component':'Apollo BLE status register/unregister 0x4abcc6/0x4abd14',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C null logging, manager identity, register/unregister child calls and manager bytes',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Manager unregister 0x5103c4 remains open','Wrapper return values not compared because mode-sync caller discards them','Final RAM placement and full image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
