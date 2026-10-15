#!/usr/bin/env python3
"""Bind four-call system-alert page style helper into selected Apollo C."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-style-round1028';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_style_4d2b9c.c'
base=root/'build/c-firmware/system-alert-page-init-round1026/apollo-main-system-alert-page-init.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'system_alert_page_style_4d2b9c.o';linked=out/'apollo-main-system-alert-page-style.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_system_alert_page_style_4d2b9c'}
assert not after-before
receipt={'round':1028,'status':'PASS_SYSTEM_ALERT_PAGE_STYLE_BINDING',
         'component':'Apollo system-alert four-call page style helper',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_call_target':'0x4d2b9c','decompiler_envelope':'0x4d2b9a',
         'validation':'Native call-order transcription, strict M55 compile and selected import binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native call order requires controlled comparison',
                  'Lower LVGL effects and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
