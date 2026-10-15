#!/usr/bin/env python3
"""Bind native silent-mode UI data callback and its two RAM bytes."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-common-data-round1016';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_common_data_46949a.c'
base=root/'build/c-firmware/cordio-wstr-round1012/apollo-main-cordio-wstr.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for literal,addr in ((0x469b88,0x2007501d),(0x469b54,0x2007501e)):
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==addr
obj=out/'silent_mode_common_data_46949a.o';linked=out/'apollo-main-silent-mode-common-data.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_uart_registry_callback_46949a'}
assert after-before=={'audio_silent_mode_status_get','audio_silent_mode_notify_app','audio_silent_mode_set_status'}
sections=subprocess.check_output(['arm-none-eabi-readelf','-SW',str(linked)],text=True)
assert '.g2.ram.silent_mode_ui_status' in sections and '.g2.ram.silent_mode_change_from_app' in sections
receipt={'round':1016,'status':'PASS_SILENT_MODE_COMMON_DATA_BINDING',
         'component':'Apollo silent-mode UI registration callback and adjacent RAM cells',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x46949a','native_cells':{'audio_silent_mode_ui_status':'0x2007501d',
                                                  'audio_silent_mode_change_from_app':'0x2007501e'},
         'validation':'Native branch transcription and literal addresses, strict M55 compile, selected binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native branch and logging effects remain to be compared',
                  'Three lower silent-mode children, RAM placement and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
