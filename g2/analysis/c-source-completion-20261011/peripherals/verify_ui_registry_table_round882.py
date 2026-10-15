#!/usr/bin/env python3
"""Verify the symbolic UI registry table and link staged callback bodies."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ui-registry-table-round882';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ui_registry_table.c'
obj=out/'ui_registry_table.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
rows=[struct.unpack_from('<4I',blob,0x6a44b0-0x438000+16*i) for i in range(43)]
assert len(rows)==43
with obj.open('rb') as f:
 elf=ELFFile(f);symtab=elf.get_section_by_name('.symtab')
 syms={s.name:s for s in symtab.iter_symbols()}
 begin,end=syms['audio_uart_display_registry_begin'],syms['audio_uart_display_registry_end']
 assert begin['st_size']==688 and end['st_value']==begin['st_value']+688
 assert begin['st_shndx']==end['st_shndx']
 data=elf.get_section(begin['st_shndx']).data()[begin['st_value']:begin['st_value']+688]
 relocs={}
 for sec in elf.iter_sections():
  if sec['sh_type'] not in ('SHT_REL','SHT_RELA') or sec['sh_info']!=begin['st_shndx']:continue
  for rel in sec.iter_relocations():
   name=symtab.get_symbol(rel['r_info_sym']).name
   relocs[rel['r_offset']-begin['st_value']]=name
 assert len(relocs)==85
 for i,(id_,primary,secondary,context) in enumerate(rows):
  offset=i*16
  assert struct.unpack_from('<I',data,offset)[0]==id_
  for field,value in ((4,primary),(8,secondary),(12,context)):
   key=offset+field;raw=struct.unpack_from('<I',data,key)[0]
   if value==0:assert raw==0 and key not in relocs,(i,field)
   else:
    assert raw==0 and key in relocs,(i,field)
    expected=(f'audio_uart_registry_callback_{value&~1:x}' if field<12 else
              f'audio_uart_registry_context_{value:08x}')
    assert relocs[key]==expected,(i,field,relocs[key],expected)
base=root/'build/c-firmware/display-registry-rows-round878/apollo-main-display-registry-rows.o'
staged=[root/'build/c-firmware'/folder/name for folder,name in (
 ('registry-callbacks-round879','registry_callback_48e484.o'),
 ('registry-callbacks-round880','registry_callbacks_small.o'),
 ('registry-callbacks-round880','registry_callback_43c400.o'),
 ('registry-callbacks-round881','registry_callback_585cca.o'),
 ('registry-callbacks-round881','registry_test_log_callbacks.o'))]
linked=out/'apollo-main-ui-registry-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),*[str(p) for p in staged],
                '-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert {'audio_uart_display_registry_begin','audio_uart_display_registry_end'}<=before
assert not {'audio_uart_display_registry_begin','audio_uart_display_registry_end'}&after
unresolved_callbacks={n for n in after if n.startswith('audio_uart_registry_callback_')}
unresolved_contexts={n for n in after if n.startswith('audio_uart_registry_context_')}
assert len(unresolved_callbacks)==56 and len(unresolved_contexts)==21
defined=subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(linked)],text=True)
for address in (0x48e484,0x46687c,0x5f9ff8,0x43c400,0x585cca,0x5cf2e6,0x5cf634,0x5cf7a8):
 assert any(line.endswith(f' audio_uart_registry_callback_{address:x}') for line in defined.splitlines())
receipt={'round':882,'status':'PASS_SYMBOLIC_UI_REGISTRY_TABLE_RELOCATABLE',
         'component':'Apollo UI listener registration table',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'stock_rows':len(rows),'pointer_relocations':len(relocs),
         'linked_callback_bodies':8,'unresolved_callback_bodies':len(unresolved_callbacks),
         'unresolved_ram_contexts':len(unresolved_contexts),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_lower_imports':sorted(after-before),'resolved_prior_imports':sorted(before-after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['56 callback bodies and 21 RAM context owners remain unresolved',
                  'Four forwarding child providers and callback ABI contracts remain open',
                  'Final ROM/RAM placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_SYMBOLIC_UI_REGISTRY',len(rows),len(relocs),len(after))
