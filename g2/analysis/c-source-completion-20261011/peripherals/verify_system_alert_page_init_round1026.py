#!/usr/bin/env python3
"""Bind native system-alert MainPage initializer and child pointer cell."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-init-round1026';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_init_4d2f48.c'
base=root/'build/c-firmware/system-alert-ui-event-round1024/apollo-main-system-alert-ui-event.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert struct.unpack_from('<I',blob,0x4d347c-0x438000)[0]==0x200749f0
obj=out/'system_alert_page_init_4d2f48.o';linked=out/'apollo-main-system-alert-page-init.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_system_alert_page_init_4d2f48'}
assert 'audio_system_alert_page_style_4d2b9c' in after-before
assert '.g2.ram.system_alert_child' in subprocess.check_output(['arm-none-eabi-readelf','-SW',str(linked)],text=True)
receipt={'round':1026,'status':'PASS_SYSTEM_ALERT_PAGE_INIT_BINDING',
         'component':'Apollo system-alert MainPage construction and child pointer cell',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d2f48','native_child_cell':'0x200749f0',
         'validation':'Native call-order transcription, strict M55 compile and selected binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'new_imports':sorted(after-before),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native call and role branches require controlled comparison',
                  'LVGL descendants, final placement and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),len(after-before),receipt['linked_sha256'])
