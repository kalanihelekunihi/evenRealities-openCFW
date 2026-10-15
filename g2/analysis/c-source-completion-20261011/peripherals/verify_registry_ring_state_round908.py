#!/usr/bin/env python3
"""Check the ring-connect state byte has a C owner in the selected link."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/registry-ring-state-round908';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/registry_ring_connect_state.c'
obj=out/'registry_ring_connect_state.o'
base=root/'build/c-firmware/registry-ring-mutex-init-round907/apollo-main-registry-ring-mutex-init.o'
linked=out/'apollo-main-registry-ring-state.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 elf=ELFFile(f);s=next(s for s in elf.get_section_by_name('.symtab').iter_symbols()
                    if s.name=='audio_registry_ring_connect_state')
 assert s['st_size']==1 and s['st_info']['bind']=='STB_GLOBAL'
 assert elf.get_section(s['st_shndx'])['sh_type']=='SHT_NOBITS'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(blob[0x5e4798-0x438000:0x5e479c-0x438000],'little')==0x2010fd1c
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_registry_ring_connect_state'} and not after-before
receipt={'round':908,'status':'PASS_RING_CONNECT_STATE_SOURCE_OWNERSHIP',
 'component':'Apollo ring-connect state byte',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),
 'native_literal':'0x5e4798','native_ram':'0x2010fd1c','symbol_size':1,
 'linked_object':str(linked.relative_to(root)),
 'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),
 'whole_image_complete':False,'hardware_proof':False,
 'gates':['Absolute placement, startup and possible indirect aliases remain open',
          'Parse buffer size and ownership, three ring-connect children, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after))
