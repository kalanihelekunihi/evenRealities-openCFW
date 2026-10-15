#!/usr/bin/env python3
"""Authenticate the C nanopb graph for RingDataRelay against the official image."""
from pathlib import Path
import hashlib
import json
import subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-pb-descriptor-round902';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_pb_descriptor.c'
obj=out/'ring_pb_descriptor.o'
base=root/'build/c-firmware/ring-buffers-round901/apollo-main-ring-buffers.o'
linked=out/'apollo-main-ring-pb-descriptor.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with obj.open('rb') as f:
 elf=ELFFile(f);symtab=elf.get_section_by_name('.symtab')
 symbols={s.name:s for s in symtab.iter_symbols()}
 ro=elf.get_section_by_name('.rodata').data()
 for name,native,size in [('ring_fields_77b104',0x7709e0,28),
                           ('ring_fields_77b134',0x77b11c,24),
                           ('ring_fields_77b14c',0x6fc80c,72)]:
  s=symbols[name];assert s['st_size']==size
  assert ro[s['st_value']:s['st_value']+size]==blob[native-0x438000:native-0x438000+size],name
 for name,native in [('audio_ring_pb_descriptor',0x77b104),
                     ('ring_pb_desc_77b134',0x77b134),('ring_pb_desc_77b14c',0x77b14c)]:
  s=symbols[name];assert s['st_size']==24
  compiled=ro[s['st_value']:s['st_value']+24]
  official=blob[native-0x438000:native-0x438000+24]
  assert compiled[8:]==official[8:],name
 reloc=elf.get_section_by_name('.rel.rodata')
 actual={r['r_offset']:int.from_bytes(ro[r['r_offset']:r['r_offset']+4],'little') for r in reloc.iter_relocations()}
 expected={
  'ring_submsgs_77b104':[(0,'ring_pb_desc_77b134'),(4,'ring_pb_desc_77b14c')],
  'audio_ring_pb_descriptor':[(0,'ring_fields_77b104'),(4,'ring_submsgs_77b104')],
  'ring_pb_desc_77b134':[(0,'ring_fields_77b134'),(4,'ring_submsgs_77b134')],
  'ring_pb_desc_77b14c':[(0,'ring_fields_77b14c'),(4,'ring_submsgs_77b14c')],
 }
 expected_reloc={symbols[owner]['st_value']+offset:symbols[target]['st_value']
                 for owner,targets in expected.items() for offset,target in targets}
 assert actual==expected_reloc,(actual,expected_reloc)
 for native,targets in [(0x77b104,[0x7709e0,0x78bd80]),
                        (0x77b134,[0x77b11c,0x78f3b0]),
                        (0x77b14c,[0x6fc80c,0x78f3b4])]:
  assert [int.from_bytes(blob[native-0x438000+i:native-0x438000+i+4],'little') for i in (0,4)]==targets
 assert [int.from_bytes(blob[0x78bd80-0x438000+i:0x78bd80-0x438000+i+4],'little') for i in (0,4,8)]==[0x77b134,0x77b14c,0]
 assert blob[0x78f3b0-0x438000:0x78f3b0-0x438000+8]==b'\0'*8
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_ring_pb_descriptor'} and not after-before
receipt={'round':902,'status':'PASS_AUTHENTICATED_RING_PB_DESCRIPTOR',
 'component':'Apollo RingDataRelay nanopb descriptor graph',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'field_words':{'root':7,'submessage_1':6,'submessage_2':18},
 'authenticated_relocations':8,'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Final ROM placement and protobuf runtime behavior outside covered callers remain open',
          'Ring fault handler, 51 registry callback bodies, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after))
