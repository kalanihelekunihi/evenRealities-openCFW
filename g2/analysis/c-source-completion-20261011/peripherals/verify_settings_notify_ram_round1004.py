#!/usr/bin/env python3
"""Bind source-owned settings notification RAM cells into selected Apollo C."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-notify-ram-round1004';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_notify_ram.c'
base=root/'build/c-firmware/settings-status-pb-descriptor-round1003/apollo-main-settings-status-pb-descriptor.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def native_word(a):return struct.unpack_from('<I',blob,a-0x438000)[0]
assert native_word(0x49bdf0)==0x200725a0
assert native_word(0x49bffc)==0x200706ec
assert native_word(0x49c030)==0x2007486c
obj=out/'settings_notify_ram.o';linked=out/'apollo-main-settings-notify-ram.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_settings_notify_encode_buffer','audio_settings_notify_staging','audio_settings_notify_magic'}
assert not after-before
sections=subprocess.check_output(['arm-none-eabi-readelf','-SW',str(linked)],text=True)
for name in ('settings_notify_encode_buffer','settings_notify_staging','settings_notify_magic'):
    assert '.g2.ram.'+name in sections
receipt={'round':1004,'status':'PASS_SETTINGS_NOTIFY_RAM_BINDING',
         'component':'Apollo settings notification staging, encode buffer and magic RAM cells',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'validation':'Native literal addresses, M55 strict compile, three selected import bindings and placement sections',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final ELF placement and full RAM-map overlap audit require the linker fragment probe',
                  'Full image/hardware proof remains open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
