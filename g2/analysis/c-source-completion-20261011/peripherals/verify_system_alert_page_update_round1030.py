#!/usr/bin/env python3
"""Bind system-alert page update and its mode/font RAM cells."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-update-round1030';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_update_4d30ba.c'
owner=root/'components/audio/uart_thread_source_candidate/registry_callback_4d2bce.c'
base=root/'build/c-firmware/system-alert-page-style-round1028/apollo-main-system-alert-page-style.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for literal,addr in ((0x4d3430,0x200749f4),(0x4d34a0,0x200746e0)):
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==addr
obj=out/'system_alert_page_update_4d30ba.o';linked=out/'apollo-main-system-alert-page-update.o'
owner_obj=out/'registry_callback_4d2bce.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(owner),'-o',str(owner_obj)],check=True)
assert '.bss.g2.ram.system_alert_message_notify' in subprocess.check_output(
    ['arm-none-eabi-readelf','-SW',str(owner_obj)],text=True)
with owner_obj.open('rb') as f:
    section=ELFFile(f).get_section_by_name('.bss.g2.ram.system_alert_message_notify')
    assert section['sh_type']=='SHT_NOBITS' and section['sh_size']==4
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_system_alert_page_update_4d30ba'}
assert {'audio_system_alert_icon_disconnect_7747e4','audio_system_alert_icon_connect_772928',
        'audio_system_alert_close_464c36'}<=after-before
receipt={'round':1030,'status':'PASS_SYSTEM_ALERT_PAGE_UPDATE_BINDING',
         'component':'Apollo system-alert page update using shared mode owner, font cell and visible icon imports',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'mode_owner_source':str(owner.relative_to(root)),
         'mode_owner_source_sha256':hashlib.sha256(owner.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d30ba','native_cells':{'mode':'0x200749f4','font':'0x200746e0'},
         'validation':'Native branch/call transcription, literal addresses, strict M55 compile and selected binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_imports':sorted(after-before),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native branch effects remain to be compared',
                  'Selected base object still carries the earlier generic BSS mode definition; full selected rebuild for exact placement remains open',
                  'Icon ROM extents, lower LVGL bodies and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),len(after-before),receipt['linked_sha256'])
