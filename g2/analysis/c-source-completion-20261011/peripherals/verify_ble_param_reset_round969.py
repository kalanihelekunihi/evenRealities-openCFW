#!/usr/bin/env python3
"""Compare the Apollo delayed BLE reset call sequence with source."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ble-param-reset-round969';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/display_ble_param_reset_delayed.c'
obj=out/'display_ble_param_reset_delayed.o'
base=root/'build/c-firmware/input-msg-record-round968/apollo-main-input-msg-record.o'
linked=out/'apollo-main-ble-param-reset.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x478252-0x438000:0x47826c-0x438000]
assert int.from_bytes(blob[0x478724-0x438000:0x478728-0x438000],'little')==0x47761d
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_ble_connect_param_request(uint8_t a){(void)a;}
uint32_t audio_event_loop_remove_delayed(void (*a)(void)){(void)a;return 0;}
void audio_event_loop_push_delayed(void (*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_param_reset_delayed_event',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for delay in (0,1,2,10000,0xffffffff):
  traces=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   callback=(syms['audio_ble_connect_param_request']|1) if compiled else 0x47761d
   hooks={(syms['audio_event_loop_remove_delayed'] if compiled else 0x476ace)&~1:'remove',
          (syms['audio_event_loop_push_delayed'] if compiled else 0x47697e)&~1:'push'}
   trace=[]
   def hook(cpu,address,size,user):
    name=hooks.get(address)
    if not name:return
    r0=cpu.reg_read(A.UC_ARM_REG_R0);assert r0==callback,(name,hex(r0),hex(callback))
    trace.append((name,cpu.reg_read(A.UC_ARM_REG_R1),cpu.reg_read(A.UC_ARM_REG_R2)) if name=='push' else (name,))
    cpu.reg_write(A.UC_ARM_REG_R0,0x8badf00d)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,hook)
   for reg,val in ((A.UC_ARM_REG_R0,delay),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
   uc.emu_start((syms['audio_ble_param_reset_delayed_event'] if compiled else 0x478252)|1,0x600000,count=100)
   traces.append(trace)
  assert traces[0]==traces[1]==[('remove',),('push',0xa4,delay)],(delay,traces)
  cases.append(delay)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_ble_param_reset_delayed_event'}
assert after-before==set()
receipt={'round':969,'status':'PASS_NATIVE_BLE_PARAM_RESET_DELAYED','component':'Apollo delayed BLE reset 0x478252',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C callback identity, removal then push, event 0xa4 and five delays',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Event-loop child providers are source owned but full image RAM placement remains open','Final terminal callback and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
