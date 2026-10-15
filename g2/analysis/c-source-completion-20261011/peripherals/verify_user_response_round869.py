#!/usr/bin/env python3
"""Verify corrected user-response C and native diagnostic literals."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/user-response-round869';out.mkdir(parents=True,exist_ok=True)
sources=[root/'components/audio/uart_thread_source_candidate'/name for name in
         ('user_response.c','user_response_log_strings.c')]
objects=[]
for src in sources:
 obj=out/(src.stem+'.o');objects.append(obj)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                 '-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'missing_module':0x442cf4,'missing_source':0x442cf0,'missing_function':0x442d10,
       'e_missing':0x442cfc,'c_missing':0x442d00,'dispatch_function':0x45b11c,
       'e_null':0x45b118,'c_null':0x45b120,'function':0x45b128,
       'e_alloc':0x45b124,'c_alloc':0x45b12c,'e_enqueue':0x45b134,'c_enqueue':0x45b138}
addresses={'audio_uart_user_'+k:struct.unpack_from('<I',blob,c-0x438000)[0] for k,c in cells.items()}
with objects[1].open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,a in addresses.items():
  s=syms[name];compiled=elf.get_section(s['st_shndx']).data()[s['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[a-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,hex(a),compiled,native)
assert struct.unpack_from('<I',blob,0x45b100-0x438000)[0]==0x77c07c
assert struct.unpack_from('<I',blob,0x45b0fc-0x438000)[0]==0x705fb8
body_imports={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(objects[0])],text=True).splitlines()}
assert {'audio_uart_user_missing_module','audio_uart_user_missing_source',
        'audio_uart_user_missing_function','audio_uart_user_dispatch_function'}<=body_imports
base=root/'build/c-firmware/sync-timer-strings-round868/apollo-main-sync-timer-strings.o'
linked=out/'apollo-main-user-response-strings.o'
subprocess.run(['arm-none-eabi-ld','-r',
                '--defsym=audio_uart_user_source=audio_uart_begin0_source',
                '--defsym=audio_uart_user_module=audio_uart_begin0_module',
                str(base),str(objects[1]),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
resolved=(set(addresses)&before)|{'audio_uart_user_source','audio_uart_user_module'}
assert before-after==resolved and not after-before
receipt={'round':869,'status':'PASS_NATIVE_USER_RESPONSE_STRINGS_AND_CORRECTED_BODY_COMPILE',
         'component':'Apollo user-response listener and enqueue diagnostics',
         'source_sha256':{str(s.relative_to(root)):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'corrected_body_compiled':True,
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Composite link retains pre-correction user_response.o; rebuild selected audio object set with corrected body',
                  'Registry RAM ownership and runtime effects remain unresolved']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_USER_RESPONSE_STRINGS_AND_BODY_COMPILE',len(addresses),len(after))
