#!/usr/bin/env python3
"""Bind the two exact native settings version byte strings into selected Apollo C."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-version-text-round1005';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_version_text.c'
base=root/'build/c-firmware/settings-notify-ram-round1004/apollo-main-settings-notify-ram.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def native(a,n):return blob[a-0x438000:a-0x438000+n]
expected={'audio_settings_right_version_text':(0x78b7bc,11),
          'audio_settings_version_text':(0x78c074,9)}
obj=out/'settings_version_text.o';linked=out/'apollo-main-settings-version-text.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
symbols=subprocess.check_output(['arm-none-eabi-nm','-S','--radix=x',str(obj)],text=True)
contents=subprocess.check_output(['arm-none-eabi-objdump','-s','-j','.rodata',str(obj)],text=True)
import re
rodata=bytes.fromhex(''.join(re.findall(r'(?m)^\s*[0-9a-f]+\s+((?:[0-9a-f]{8}\s*)+)',contents)).replace(' ',''))
for name,(addr,size) in expected.items():
    match=re.search(r'(?m)^([0-9a-f]+)\s+([0-9a-f]+)\s+R\s+'+name+r'$',symbols)
    assert match,(name,symbols)
    off,actual_size=(int(x,16) for x in match.groups())
    assert actual_size==size
    assert rodata[off:off+size]==native(addr,size),(name,rodata[off:off+size],native(addr,size))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after==set(expected)
assert not after-before
receipt={'round':1005,'status':'PASS_SETTINGS_VERSION_TEXT_BINDING',
         'component':'Apollo settings version ROM byte strings',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_spans':{name:{'address':hex(addr),'size':size} for name,(addr,size) in expected.items()},
         'validation':'Byte-exact native ROM spans, strict M55 compile, and two selected import bindings',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final ROM placement and whole-image layout remain open','Full image/hardware proof remains open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
