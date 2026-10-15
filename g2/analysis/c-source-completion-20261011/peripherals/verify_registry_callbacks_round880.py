#!/usr/bin/env python3
"""Compile three small UI callbacks and compare their native contracts."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-callbacks-round880';out.mkdir(parents=True,exist_ok=True)
names=('registry_callbacks_small.c','registry_callback_43c400.c')
sources=[root/'components/audio/uart_thread_source_candidate'/name for name in names]
objects=[]
for src in sources:
 obj=out/(src.stem+'.o');objects.append(obj)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                 '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                 '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
fmap={int(d['entry'],16):d for d in map(json.loads,(root/'research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
addresses=(0x46687c,0x5f9ff8,0x43c400)
native={}
for addr in addresses:
 d=fmap[addr];code=blob[addr-0x438000:addr+d['body_bytes']-0x438000]
 assert hashlib.sha256(code).hexdigest()==d['body_sha256']
 native[addr]=code
rows=[struct.unpack_from('<4I',blob,0x6a44b0-0x438000+16*i) for i in range(43)]
assert all(any((v&~1)==a for row in rows for v in row[1:3] if v) for a in addresses)
def execute(addr,child,event,payload,length):
 code=native[addr];end=addr+len(code)
 uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for page in {addr&~0xfff,(end-1)&~0xfff,child&~0xfff}:uc.mem_map(page,0x1000)
 uc.mem_write(addr,code);uc.mem_write(child,b'\x70\x47')
 uc.mem_map(0x20000000,0x1000)
 uc.reg_write(A.UC_ARM_REG_R0,event)
 uc.reg_write(A.UC_ARM_REG_R1,payload)
 uc.reg_write(A.UC_ARM_REG_R2,length)
 uc.reg_write(A.UC_ARM_REG_SP,0x20000800)
 uc.reg_write(A.UC_ARM_REG_LR,end|1)
 calls=[]
 def hook(cpu,address,size,user):
  if address==child:calls.append([cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)])
 uc.hook_add(UC_HOOK_CODE,hook)
 uc.emu_start(addr|1,end,count=30)
 assert uc.reg_read(A.UC_ARM_REG_R0)==0
 return calls
observations=[]
for event,payload,length in ((5,0x12345678,0x87654321),(0,0xffffffff,0xffffffff)):
 calls=execute(0x46687c,0x466412,event,payload,length)
 assert calls==([[payload,length]] if event==5 else [])
 observations.append({'callback':'0x46687c','input':[event,payload,length],'calls':calls})
for event,payload,length in ((0,0,0),(9,0x12345678,0x87654321)):
 calls=execute(0x5f9ff8,0x4c548c,event,payload,length)
 assert calls==[[payload,length&0xffff]]
 observations.append({'callback':'0x5f9ff8','input':[event,payload,length],'calls':calls})
cells={'audio_uart_registry_aging_extended':0x43c758,
       'audio_uart_registry_aging_function':0x43c75c,
       'audio_uart_registry_aging_source':0x43c760,
       'audio_uart_registry_aging_module':0x43c764,
       'audio_uart_registry_aging_compact':0x43c768}
with objects[1].open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,cell in cells.items():
  addr=struct.unpack_from('<I',blob,cell-0x438000)[0]
  sym=syms[name]
  data=elf.get_section(sym['st_shndx']).data()[sym['st_value']:].split(b'\0',1)[0]+b'\0'
  assert data==blob[addr-0x438000:].split(b'\0',1)[0]+b'\0',(name,hex(addr))
providers=set();imports=set()
for obj in objects:
 providers|={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines()}
 imports|={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()}
assert {f'audio_uart_registry_callback_{a:x}' for a in addresses}<=providers
assert {'audio_uart_registry_child_466412','audio_uart_registry_child_4c548c'}<=imports
selected=root/'build/c-firmware/display-registry-rows-round878/apollo-main-display-registry-rows.o'
selected_imports={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(selected)],text=True).splitlines()}
assert len(selected_imports)==532
receipt={'round':880,'status':'PASS_THREE_SMALL_REGISTRY_CALLBACK_C_BODIES',
         'component':'Apollo UI registry callbacks',
         'sources_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':{hex(a):hashlib.sha256(native[a]).hexdigest() for a in addresses},
         'native_aging_strings':{k:hex(struct.unpack_from('<I',blob,v-0x438000)[0]) for k,v in cells.items()},
         'observations':observations,'compiled_callback_bodies_this_round':len(addresses),
         'compiled_callback_bodies_cumulative':4,'selected_link_unresolved':len(selected_imports),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Callback table remains to be emitted with relocatable C entries',
                  'Three other callback child bodies and remaining table handlers remain unresolved',
                  'Staged callbacks are not yet linked into selected Apollo composition']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_THREE_REGISTRY_CALLBACKS',len(addresses),len(selected_imports))
