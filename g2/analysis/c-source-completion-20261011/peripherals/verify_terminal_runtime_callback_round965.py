#!/usr/bin/env python3
"""Native/C Apollo BLE-status callback used by terminal mode sync."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-runtime-callback-round965';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_runtime_event_callback_1.c'
obj=out/'terminal_runtime_event_callback_1.o'
base=root/'build/c-firmware/terminal-mode-sync-round964/apollo-main-terminal-mode-sync.o'
linked=out/'apollo-main-terminal-runtime-callback.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5e8814-0x438000:0x5e8846-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
void audio_td_notify_state_clear(void){}
void audio_td_session_struct_clear(void){}
void audio_terminal_request_runtime_event_if_allowed(uint32_t x){(void)x;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_runtime_event_callback_1',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'notify':'audio_td_notify_state_clear','clear':'audio_td_session_struct_clear','request':'audio_terminal_request_runtime_event_if_allowed'}
 native_addrs={'notify':0x597110,'clear':0x597124,'request':0x5e873e}
 cases=[]
 for event in (0,1,255):
  for present in (False,True):
   for status in (0,1,2,255):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
     uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     payload=0x20010000;uc.mem_write(payload,bytes([status]))
     hooks={((syms[names[k]] if compiled else addr)&~1):k for k,addr in native_addrs.items()}
     calls=[]
     def hook(cpu,address,size,user):
      name=hooks.get(address)
      if not name:return
      calls.append((name,cpu.reg_read(A.UC_ARM_REG_R0) if name=='request' else None))
      cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,payload if present else 0),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start(((syms['audio_terminal_runtime_event_callback_1'] if compiled else 0x5e8814)|1),0x600000,count=100)
     outputs.append(tuple(calls))
    assert outputs[0]==outputs[1],(event,present,status,outputs)
    cases.append((event,present,status))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_runtime_event_callback_1'} and not after-before
receipt={'round':965,'status':'PASS_NATIVE_TERMINAL_RUNTIME_CALLBACK','component':'Apollo BLE-status terminal callback 0x5e8814','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'validation':'Native/C event and payload gates, state clear and runtime-event child order','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Mode-sync provider children and final agent-content callback remain open','49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
