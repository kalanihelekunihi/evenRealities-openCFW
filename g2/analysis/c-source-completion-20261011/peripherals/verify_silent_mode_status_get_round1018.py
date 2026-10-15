#!/usr/bin/env python3
"""Bind native settings config pointer and silent-mode status getter."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-status-get-round1018';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_status_get_46919e.c'
base=root/'build/c-firmware/silent-mode-common-data-round1016/apollo-main-silent-mode-common-data.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert struct.unpack_from('<I',blob,0x46bee8-0x438000)[0]==0x20072da8
obj=out/'silent_mode_status_get_46919e.o';linked=out/'apollo-main-silent-mode-status-get.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_silent_mode_status_get'}
assert not after-before
receipt={'round':1018,'status':'PASS_SILENT_MODE_STATUS_GET_BINDING',
         'component':'Apollo settings config pointer getter and silent-mode status getter',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entries':['0x46b44c','0x46919e'],'native_config_ram':'0x20072da8',
         'validation':'Native literal, strict M55 compile and selected import binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native status behavior requires a controlled oracle',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
