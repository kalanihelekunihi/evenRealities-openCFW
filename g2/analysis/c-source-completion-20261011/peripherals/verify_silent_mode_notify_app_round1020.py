#!/usr/bin/env python3
"""Bind native silent-mode nanopb notification producer."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-notify-app-round1020';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_notify_app_49bf24.c'
base=root/'build/c-firmware/silent-mode-status-get-round1018/apollo-main-silent-mode-status-get.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'silent_mode_notify_app_49bf24.o';linked=out/'apollo-main-silent-mode-notify-app.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_silent_mode_notify_app'}
assert not after-before
receipt={'round':1020,'status':'PASS_SILENT_MODE_NOTIFY_APP_BINDING',
         'component':'Apollo silent-mode nanopb notification packet producer',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x49bf24','packet_bytes':104,
         'validation':'Native packet/log transcription, strict M55 compile and selected import binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native packet effects remain to be compared',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
