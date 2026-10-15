#!/usr/bin/env python3
"""Bind native system-alert UI event callback and three RAM cells."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-ui-event-round1024';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_ui_event_4d3354.c'
base=root/'build/c-firmware/silent-mode-set-status-round1022/apollo-main-silent-mode-set-status.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for literal,addr in ((0x4d34b8,0x20003bd0),(0x4d3478,0x200749ec),
                     (0x4d3440,0x20075025),(0x4d3444,0x20003bcc)):
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==addr
obj=out/'system_alert_ui_event_4d3354.o';linked=out/'apollo-main-system-alert-ui-event.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_uart_registry_callback_4d3354'}
assert after-before=={'audio_system_alert_page_init_4d2f48','audio_system_alert_page_update_4d30ba'}
sections=subprocess.check_output(['arm-none-eabi-readelf','-SW',str(linked)],text=True)
for name in ('system_alert_page_id','system_alert_active','system_alert_parent'):
    assert '.g2.ram.'+name in sections
receipt={'round':1024,'status':'PASS_SYSTEM_ALERT_UI_EVENT_BINDING',
         'component':'Apollo system-alert UI create/update/exit callback and RAM cells',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d3354','native_cells':{'page_id':'0x20003bcc',
                     'registry_context':'0x20003bd0','parent':'0x200749ec','active':'0x20075025'},
         'validation':'Native literal addresses/store widths, strict M55 compile and selected binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual compiled-C/native branch effects remain to be compared',
                  'Two page children, registry context ownership and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
