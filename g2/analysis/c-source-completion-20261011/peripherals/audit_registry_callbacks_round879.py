#!/usr/bin/env python3
"""Inventory Apollo UI registration callbacks and verify one C body."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-callbacks-round879';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_callback_48e484.c'
obj=out/'registry_callback_48e484.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
providers={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines()}
imports={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()}
assert 'audio_uart_registry_callback_48e484' in providers
assert imports=={'audio_uart_registry_child_497960'}
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
start,end=0x6a44b0,0x6a4760
rows=[struct.unpack_from('<4I',blob,start-0x438000+i*16) for i in range((end-start)//16)]
assert len(rows)==43 and rows[33][1]==0x48e485
callbacks=sorted({v&~1 for row in rows for v in row[1:3] if v})
assert len(callbacks)==64
function_map={int(d['entry'],16):d for d in map(json.loads,(root/'research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
mapped=[a for a in callbacks if a in function_map]
decompiled=[a for a in mapped if function_map[a]['decompiled']]
assert len(mapped)==60 and len(decompiled)==59
native=blob[0x48e484-0x438000:0x48e494-0x438000]
assert native.hex()=='80b50800110089b209f068fa002002bd'
assert hashlib.sha256(native).hexdigest()==function_map[0x48e484]['body_sha256']
assert function_map[0x48e484]['callees']==['00497960']
observations=[]
for ignored,payload,length in ((0,0,0),(1,0x12345678,0x87654321),
                               (0xffffffff,0xffffffff,0xffffffff)):
 uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 uc.mem_map(0x48e000,0x1000);uc.mem_write(0x48e484,native)
 uc.mem_map(0x497000,0x1000);uc.mem_write(0x497960,b'\x70\x47')
 uc.mem_map(0x20000000,0x1000)
 uc.reg_write(A.UC_ARM_REG_R0,ignored)
 uc.reg_write(A.UC_ARM_REG_R1,payload)
 uc.reg_write(A.UC_ARM_REG_R2,length)
 uc.reg_write(A.UC_ARM_REG_SP,0x20000800)
 uc.reg_write(A.UC_ARM_REG_LR,0x48e495)
 seen=[]
 def hook(cpu,address,size,user):
  if address==0x497960:
   seen.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
 uc.hook_add(UC_HOOK_CODE,hook)
 uc.emu_start(0x48e485,0x48e494,count=20)
 assert seen==[(payload,length&0xffff)] and uc.reg_read(A.UC_ARM_REG_R0)==0
 observations.append({'input':[ignored,payload,length],'child_args':list(seen[0]),'return_r0':0})
inventory={'stock_rows':len(rows),'unique_callback_entries':len(callbacks),
           'function_map_matches':len(mapped),'decompiled_matches':len(decompiled),
           'mapped_body_bytes':sum(function_map[a]['body_bytes'] for a in mapped),
           'unmapped':[hex(a) for a in callbacks if a not in function_map],
           'not_decompiled':[hex(a) for a in mapped if not function_map[a]['decompiled']],
           'rows':[{'id':hex(r[0]),'primary':hex(r[1]),'secondary':hex(r[2]),
                    'context':hex(r[3])} for r in rows]}
(out/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
selected=root/'build/c-firmware/display-registry-rows-round878/apollo-main-display-registry-rows.o'
selected_imports={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(selected)],text=True).splitlines()}
assert len(selected_imports)==532
receipt={'round':879,'status':'PASS_REGISTRY_CALLBACK_INVENTORY_AND_ONE_C_BODY',
         'component':'Apollo UI registration callbacks',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'compiled_object':str(obj.relative_to(root)),'compiled_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'observations':observations,'inventory':str((out/'inventory.json').relative_to(root)),
         'inventory_sha256':hashlib.sha256((out/'inventory.json').read_bytes()).hexdigest(),
         'unique_callbacks':len(callbacks),'function_map_matches':len(mapped),
         'decompiled_matches':len(decompiled),'compiled_callback_bodies_this_round':1,
         'selected_link_unresolved':len(selected_imports),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Registry callback table is not yet emitted as relocatable C data',
                  'Other callback bodies and child 0x497960 remain unresolved',
                  'No selected-link import count change in this staged body round']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_REGISTRY_CALLBACK_AUDIT',len(rows),len(callbacks),len(mapped),len(decompiled))
