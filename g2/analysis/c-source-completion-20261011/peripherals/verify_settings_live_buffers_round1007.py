#!/usr/bin/env python3
"""Bind minimum evidenced settings RAM buffers without claiming full extents."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-live-buffers-round1007';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_live_buffers.c'
base=root/'build/c-firmware/settings-runtime-cells-round1006/apollo-main-settings-runtime-cells.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
expected={'audio_settings_config_live':(0x20072da8,0x50,0x46bee8),
          'audio_settings_last_message_state':(0x20072608,0x68,0x4672f8)}
assert struct.unpack_from('<I',blob,0x49bdf4-0x438000)[0]==0x20072608
assert struct.unpack_from('<H',blob,0x49b404-0x438000)[0]==0x2268
for name,(addr,_,literal) in expected.items():
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==addr,name
obj=out/'settings_live_buffers.o';linked=out/'apollo-main-settings-live-buffers.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
symbols=subprocess.check_output(['arm-none-eabi-nm','-S',str(obj)],text=True)
for name,(_,size,_) in expected.items():
    rows=[line.split() for line in symbols.splitlines() if line.endswith(' '+name)]
    assert len(rows)==1 and int(rows[0][1],16)==size,(name,rows)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after==set(expected)
assert not after-before
receipt={'round':1007,'status':'PASS_SETTINGS_LIVE_BUFFER_MINIMA_BINDING',
         'component':'Apollo settings live config and last-message buffer minimum spans',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_minimum_spans':{name:{'address':hex(addr),'minimum_size':size,'literal':hex(literal)} for name,(addr,size,literal) in expected.items()},
         'validation':'Authenticated native literal addresses, 0x68-byte stock copy callsite, strict M55 compile and selected import bindings',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Actual allocation extents and final RAM placement are not yet proven',
                  'Full RAM map overlap audit and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
