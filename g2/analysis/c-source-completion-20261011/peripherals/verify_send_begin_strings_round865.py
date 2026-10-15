#!/usr/bin/env python3
"""Match compiled Apollo UART listener strings against official image bytes."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/send-begin-strings-round865';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/send_begin_log_strings.c'
obj=out/'send_begin_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={}
for i in (0,1,3,4):
 native[f'audio_uart_begin{i}_module']=0x77c07c
 native[f'audio_uart_begin{i}_source']=0x705fb8
native.update({
 'audio_uart_begin0_function':0x74ed1c,'audio_uart_begin1_function':0x77c13c,
 'audio_uart_begin3_function':0x75a7a0,'audio_uart_begin4_function':0x783c44,
 'audio_uart_begin_e_null':0x7440f4,'audio_uart_begin_c_null':0x706370,
 'audio_uart_begin_e_event':0x783be0,'audio_uart_begin_c_event':0x743f94,
 'audio_uart_begin_e_userdata':0x783c58,'audio_uart_begin_c_userdata':0x74ecf4,
 'audio_uart_begin_e_submit':0x783c6c,'audio_uart_begin_c_submit':0x744120,
 'audio_uart_begin0_e_received':0x744178,'audio_uart_begin0_c_received':0x70f8a4,
 'audio_uart_begin1_e_received':0x772730,'audio_uart_begin1_c_received':0x72e1ec,
 'audio_uart_begin3_e_received':0x7658d0,'audio_uart_begin3_c_received':0x7238c0,
 'audio_uart_begin4_e_received':0x7726f8,'audio_uart_begin4_c_received':0x72e1b8})
assert len(native)==28
with obj.open('rb') as f:
 elf=ELFFile(f);symtab=elf.get_section_by_name('.symtab')
 syms={s.name:s for s in symtab.iter_symbols()}
 for name,addr in native.items():
  sym=syms[name];section=elf.get_section(sym['st_shndx']);raw=section.data()[sym['st_value']:]
  compiled=raw.split(b'\0',1)[0]+b'\0'
  stock=blob[addr-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==stock,(name,compiled,stock)
 for suffix in ('module','source'):
  assert len({(syms[f'audio_uart_begin{i}_{suffix}']['st_shndx'],syms[f'audio_uart_begin{i}_{suffix}']['st_value']) for i in (0,1,3,4)})==1
base=root/'build/c-firmware/audio-excluded-dirs-round864/apollo-main-expanded-selected-source.o'
linked=out/'apollo-main-send-begin-strings.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(native)<=before and not set(native)&after
assert len(before-after)==28 and not after-before,(len(before-after),after-before)
receipt={'round':865,'status':'PASS_EXACT_NATIVE_STRING_CONTENTS','component':'Apollo UART listener diagnostic strings',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in native.items()},
         'matched_strings':len(native),'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Exact string contents and shared symbol addresses do not prove complete listener runtime behavior',
                  'Final ROM placement and whole image link remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_SEND_BEGIN_NATIVE_STRINGS',len(native),len(after))
