#!/usr/bin/env python3
"""Authenticate the Apollo terminal command handler table as C relocations."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-command-table-round911';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_handlers_72eb78.c'
obj=out/'terminal_command_handlers_72eb78.o'
base=root/'build/c-firmware/registry-ring-check-round910/apollo-main-registry-ring-check.o'
linked=out/'apollo-main-terminal-command-table.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert struct.unpack_from('<I',blob,0x5ea218-0x438000)[0]==0x72eb78
targets=struct.unpack_from('<13I',blob,0x72eb78-0x438000)
assert targets==(0,0x5e8847,0x5e8c49,0x5e8e6d,0x5e9065,0x5e9391,0x5e9901,
                 0x5e9ab9,0x5e9b09,0x5e9c79,0x5e9e63,0x5e9ec9,0x5e9f75)
with obj.open('rb') as f:
 elf=ELFFile(f);symtab=elf.get_section_by_name('.symtab')
 symbol=next(s for s in symtab.iter_symbols() if s.name=='audio_terminal_command_handlers')
 assert symbol['st_size']==52
 section=elf.get_section(symbol['st_shndx'])
 data=section.data()[symbol['st_value']:symbol['st_value']+52]
 assert struct.unpack_from('<I',data)[0]==0
 reloc=[]
 for s in elf.iter_sections():
  if s['sh_type'] in ('SHT_REL','SHT_RELA') and s['sh_info']==symbol['st_shndx']:
   reloc.extend(r for r in s.iter_relocations()
                if symbol['st_value']<=r['r_offset']<symbol['st_value']+52)
 assert len(reloc)==12
 assert sorted(r['r_offset']-symbol['st_value'] for r in reloc)==[4*i for i in range(1,13)]
 assert {r['r_offset']-symbol['st_value']:symtab.get_symbol(r['r_info_sym']).name
         for r in reloc}=={4*i:f'audio_terminal_command_{(targets[i]&~1):x}'
                           for i in range(1,13)}
 names={sym.name for sym in symtab.iter_symbols() if sym.name and sym['st_shndx']=='SHN_UNDEF'}
 assert names=={f'audio_terminal_command_{(v&~1):x}' for v in targets[1:]}
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert after-before=={f'audio_terminal_command_{(v&~1):x}' for v in targets[1:]}
receipt={'round':911,'status':'PASS_AUTHENTICATED_TERMINAL_COMMAND_TABLE',
 'component':'Apollo terminal command ROM callback table 0x72eb78',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_table_sha256':hashlib.sha256(blob[0x72eb78-0x438000:0x72eb78-0x438000+52]).hexdigest(),
 'rows':13,'pointer_relocations':len(reloc),
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Twelve terminal command callback bodies and route dispatcher remain open',
          'Runtime event-name RAM array, ring-connect parse buffer, 49 registry callbacks, final placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(reloc),len(before),len(after))
