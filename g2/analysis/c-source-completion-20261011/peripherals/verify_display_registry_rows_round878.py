#!/usr/bin/env python3
"""Verify UI listener registry RAM capacity and selected C link."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/display-registry-rows-round878';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/display_registry_rows.c'
obj=out/'display_registry_rows.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert word(0x442cd8)==0x20066230
assert word(0x442d14)==0x6a44b0 and word(0x442d18)==0x6a4760
assert (0x6a4760-0x6a44b0)//16==43
assert (word(0x75d3d0),word(0x75d3cc))==(0x20004558,0x70af0)
assert 0x20004558<=0x20066230 and 0x20066230+0x800<=0x20075048
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 sym=syms['audio_uart_user_registry_rows']
 assert sym['st_size']==0x800 and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS'
base=root/'build/c-firmware/master-prepare-data-round877/apollo-main-master-data-source.o'
linked=out/'apollo-main-display-registry-rows.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_uart_user_registry_rows'} and not after-before
receipt={'round':878,'status':'PASS_NATIVE_UI_REGISTRY_RAM_CAPACITY',
         'component':'Apollo UI listener registry',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_ram_address':'0x20066230','capacity_rows':128,'stock_rom_rows':43,
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['ROM callback registration table and scheduler thread body remain unresolved',
                  'Final RAM placement, whole-image layout, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_DISPLAY_REGISTRY_ROWS',len(after))
