#!/usr/bin/env python3
"""Bind five native-addressed settings scalar/handle cells into selected Apollo C."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-runtime-cells-round1006';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_runtime_cells.c'
base=root/'build/c-firmware/settings-version-text-round1005/apollo-main-settings-version-text.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
expected={
 'audio_settings_left_version_last_request_tick':(0x20074994,4,0x46c40c),
 'audio_settings_ancc_mutex':(0x2007491c,4,0x497938),
 'audio_settings_ancc_count':(0x2007500d,1,0x497d24),
 'audio_settings_peer_send_queue':(0x200749cc,4,0x45d068),
 'audio_settings_peer_event':(0x20074b10,4,0x45d0c8)}
for name,(addr,_,literal) in expected.items():
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==addr,name
obj=out/'settings_runtime_cells.o';linked=out/'apollo-main-settings-runtime-cells.o'
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
assert before-after==set(expected),(before-after,set(expected))
assert not after-before
sections=subprocess.check_output(['arm-none-eabi-readelf','-SW',str(linked)],text=True)
for name in expected:assert '.g2.ram.'+name.removeprefix('audio_') in sections,name
receipt={'round':1006,'status':'PASS_SETTINGS_RUNTIME_CELLS_BINDING',
         'component':'Apollo settings tick, ANCC count/mutex and peer transport handle cells',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_cells':{name:{'address':hex(addr),'size':size,'literal':hex(literal)} for name,(addr,size,literal) in expected.items()},
         'validation':'Authenticated native literal addresses, strict M55 compile, selected import bindings and sections',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final exact RAM placement and full RAM map overlap audit remain open',
                  'OS handle producer initialization and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
