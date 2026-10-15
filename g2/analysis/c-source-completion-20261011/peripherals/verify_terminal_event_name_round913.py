#!/usr/bin/env python3
"""Native/C terminal event name lookup with explicit RAM array dependency."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-event-name-round913';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_event_name_5ea004.c'
obj=out/'terminal_event_name_5ea004.o'
base=root/'build/c-firmware/terminal-command-route-round912/apollo-main-terminal-command-route.o'
linked=out/'apollo-main-terminal-event-name.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5ea004-0x438000:0x5ea01a-0x438000]
assert int.from_bytes(blob[0x5ea1fc-0x438000:0x5ea200-0x438000],'little')==0x77c97c
assert int.from_bytes(blob[0x5ea200-0x438000:0x5ea204-0x438000],'little')==0x20003e6c
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('const char *audio_terminal_event_names[13];\n')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_event_name_5ea004',
                 str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
       if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for event in list(range(256))+[0x100,0x101,0x10c,0xffffffff]:
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x100000)
   array=syms['audio_terminal_event_names'] if compiled else 0x20003e6c
   for i in range(13):
    p=0x20078000+16*i
    uc.mem_write(p,('EVENT_%02d'%i).encode()+b'\0')
    uc.mem_write(array+4*i,p.to_bytes(4,'little'))
   for reg,val in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_SP,0x200ff000),
                   (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
   uc.emu_start(((syms['audio_terminal_event_name_5ea004'] if compiled else 0x5ea004)|1),
                0x600000,count=100)
   result=uc.reg_read(A.UC_ARM_REG_R0)
   outputs.append(bytes(uc.mem_read(result,64)).split(b'\0')[0].decode('ascii'))
  assert outputs[0]==outputs[1],(event,outputs)
  cases.append(event)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_event_name_5ea004'}
assert after-before=={'audio_terminal_event_names'}
receipt={'round':913,'status':'PASS_NATIVE_TERMINAL_EVENT_NAME_LOOKUP',
 'component':'Apollo terminal event-name helper 0x5ea004',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'all_event_bytes':True,'native_array':'0x20003e6c',
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Runtime event-name array ownership and initialization remain open',
          'Twelve terminal callback bodies, ring-connect parse buffer, 49 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
