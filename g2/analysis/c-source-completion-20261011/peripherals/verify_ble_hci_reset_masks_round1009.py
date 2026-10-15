#!/usr/bin/env python3
"""Bind byte-exact Apollo HCI reset command masks into selected C."""
from pathlib import Path
import hashlib,json,re,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ble-hci-reset-masks-round1009';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ble_hci_reset_masks.c'
base=root/'build/c-firmware/settings-manager-storage-round1008/apollo-main-settings-manager-storage.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
expected={'audio_ble_hci_event_mask_78d6dc':0x78d6dc,
          'audio_ble_hci_le_event_mask_78d6e4':0x78d6e4,
          'audio_ble_hci_event_mask_page2_78d6ec':0x78d6ec}
obj=out/'ble_hci_reset_masks.o';linked=out/'apollo-main-ble-hci-reset-masks.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
symbols=subprocess.check_output(['arm-none-eabi-nm','-S','--radix=x',str(obj)],text=True)
contents=subprocess.check_output(['arm-none-eabi-objdump','-s','-j','.rodata',str(obj)],text=True)
rodata=bytes.fromhex(''.join(re.findall(r'(?m)^\s*[0-9a-f]+\s+((?:[0-9a-f]{8}\s*)+)',contents)).replace(' ',''))
for name,addr in expected.items():
    match=re.search(r'(?m)^([0-9a-f]+)\s+([0-9a-f]+)\s+R\s+'+name+r'$',symbols)
    assert match,name
    off,size=(int(x,16) for x in match.groups())
    assert size==8 and rodata[off:off+8]==blob[addr-0x438000:addr-0x438000+8],name
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after==set(expected)
assert not after-before
receipt={'round':1009,'status':'PASS_BLE_HCI_RESET_MASKS_BINDING',
         'component':'Apollo BLE HCI reset command mask ROM data',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_spans':{name:{'address':hex(addr),'size':8} for name,addr in expected.items()},
         'validation':'Byte-exact native ROM spans, strict M55 compile, three selected import bindings',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final ROM placement and broader HCI reset behavior remain open',
                  'Full image/hardware proof remains open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
