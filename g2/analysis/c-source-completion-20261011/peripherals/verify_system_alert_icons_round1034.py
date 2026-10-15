#!/usr/bin/env python3
"""Verify byte-exact system-alert icon assets and bind their descriptors."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-icons-round1034';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_icons.c'
base=root/'build/c-firmware/system-alert-close-round1032/apollo-main-system-alert-close.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'system_alert_icons.o';linked=out/'apollo-main-system-alert-icons.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
assets=(('disconnect',0x7747e4,0x6bb6c0),('connect',0x772928,0x6ba700))
for name,descriptor,data in assets:
    sec=f'.g2.rom.system_alert_pixels_{name}'
    dumped=out/f'{name}.bin'
    subprocess.run(['arm-none-eabi-objcopy','--dump-section',f'{sec}={dumped}',str(obj)],check=True)
    assert dumped.read_bytes()==blob[data-0x438000:data-0x438000+0x240],name
    dsc=out/f'{name}-descriptor.bin'
    subprocess.run(['arm-none-eabi-objcopy','--dump-section',
                    f'.g2.rom.system_alert_icon_{name}={dsc}',str(obj)],check=True)
    raw=dsc.read_bytes();native=blob[descriptor-0x438000:descriptor-0x438000+28]
    assert len(raw)==28 and raw[:16]==native[:16] and raw[20:]==native[20:]
    assert struct.unpack_from('<I',native,16)[0]==data
    assert struct.unpack_from('<I',raw,16)[0]==0
    relocation=subprocess.check_output(['arm-none-eabi-readelf','-rW',str(obj)],text=True)
    assert f'audio_system_alert_pixels_{name}_{data:06x}' in relocation
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
expected={f'audio_system_alert_icon_{name}_{descriptor:06x}' for name,descriptor,_ in assets}
assert before-after==expected and not after-before
receipt={'round':1034,'status':'PASS_SYSTEM_ALERT_ICONS_BINDING',
         'component':'Apollo system-alert source-owned LVGL descriptors and pixel arrays',
         'generator':'analysis/c-source-completion-20261011/peripherals/generate_system_alert_icons.py',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'assets':{name:{'descriptor':hex(d),'pixels':hex(p),'pixel_bytes':0x240} for name,d,p in assets},
         'validation':'Exact native pixel bytes, descriptor nonpointer fields, pointer relocation, strict M55 compile and selected binding',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final descriptor/pixel ROM placement and full ROM overlap audit remain open',
                  'Lower LVGL runtime and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
