#!/usr/bin/env python3
"""Bind the hand record's two C names to one zero-initialized storage owner."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-hand-storage-round886';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_hand_storage.c'
obj=out/'registry_hand_storage.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
word=lambda addr:struct.unpack_from('<I',blob,addr-0x438000)[0]
native_address=word(0x4667ec)
start,length=word(0x75d3d0),word(0x75d3cc)
assert (native_address,start,length)==(0x200736d4,0x20004558,0x70af0)
assert start<=native_address and native_address+0x30<=start+length
with obj.open('rb') as f:
 elf=ELFFile(f)
 syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 record=syms['audio_uart_hand_record'];context=syms['audio_uart_hand_context']
 assert record['st_size']==0x30 and elf.get_section(record['st_shndx'])['sh_type']=='SHT_NOBITS'
 assert context['st_size']==4
 rela=[s for s in elf.iter_sections() if s['sh_type'] in ('SHT_REL','SHT_RELA')]
 targets=[]
 for section in rela:
  symtab=elf.get_section(section['sh_link'])
  targets.extend(symtab.get_symbol(rel['r_info_sym']).name for rel in section.iter_relocations())
 assert 'audio_uart_hand_record' in targets,targets
base=root/'build/c-firmware/registry-child-round885/apollo-main-registry-child.o'
linked=out/'apollo-main-registry-hand-storage.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_hand_record','audio_uart_hand_context'} and not after-before
receipt={'round':886,'status':'PASS_NATIVE_HAND_STORAGE_OWNER',
         'component':'Apollo universal-setting hand record',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_record_address':hex(native_address),'native_record_size':0x30,
         'native_startup_zero_range':[hex(start),hex(start+length)],
         'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final linker placement at native RAM address is unproven',
                  'Snapshot context and 56 registry callback bodies remain open',
                  'Boot and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_HAND_STORAGE_OWNER',len(after))
