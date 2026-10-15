#!/usr/bin/env python3
"""Link two source-owned icon descriptors/pixels at exact native ROM spans."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-icons-placement-round1035';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_icons.c'
linker=root/'components/audio/uart_thread_source_candidate/system_alert_icons.ld'
obj=root/'build/c-firmware/system-alert-icons-round1034/system_alert_icons.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
elf=out/'probe.elf'
subprocess.run(['arm-none-eabi-ld','-T',str(linker),'-o',str(elf),str(obj)],check=True)
expected={'system_alert_pixels_connect':(0x6ba700,0x240),
          'system_alert_pixels_disconnect':(0x6bb6c0,0x240),
          'system_alert_icon_connect':(0x772928,28),
          'system_alert_icon_disconnect':(0x7747e4,28)}
with elf.open('rb') as f:
    image=ELFFile(f)
    spans=[]
    for name,(address,size) in expected.items():
        section=image.get_section_by_name('.g2.rom.'+name)
        assert section is not None and section['sh_addr']==address and section['sh_size']==size,name
        actual=section.data();native=blob[address-0x438000:address-0x438000+size]
        assert actual==native,(name,actual.hex(),native.hex())
        spans.append((address,address+size,name))
spans.sort()
assert all(spans[i][1]<=spans[i+1][0] for i in range(len(spans)-1))
receipt={'round':1035,'status':'PASS_SYSTEM_ALERT_ICONS_ROM_PLACEMENT',
         'component':'Apollo system-alert icons exact ROM probe placement',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'linker':str(linker.relative_to(root)),'linker_sha256':hashlib.sha256(linker.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'spans':{name:{'address':hex(a),'size':n} for name,(a,n) in expected.items()},
         'validation':'Linked ELF section addresses and every byte match official ROM; four spans do not overlap each other',
         'probe_elf':str(elf.relative_to(root)),'probe_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Full ROM map overlap audit and final image link remain open',
                  'Lower LVGL runtime and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['probe_sha256'])
