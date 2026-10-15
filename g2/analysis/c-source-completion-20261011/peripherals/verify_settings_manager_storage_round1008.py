#!/usr/bin/env python3
"""Bind shared Apollo manager record and its five native-addressed aliases."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-manager-storage-round1008';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_manager_storage.c'
base=root/'build/c-firmware/settings-live-buffers-round1007/apollo-main-settings-live-buffers.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for literal in (0x44a40c,0x4667f0,0x46c694,0x4f5e80):
    assert struct.unpack_from('<I',blob,literal-0x438000)[0]==0x200036fc
obj=out/'settings_manager_storage.o';linked=out/'apollo-main-settings-manager-storage.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
def symbols(path):
    found={}
    for line in subprocess.check_output(['arm-none-eabi-nm',str(path)],text=True).splitlines():
        parts=line.split()
        if len(parts)==3:found[parts[2]]=int(parts[0],16)
    return found
sym=symbols(obj);base_addr=sym['audio_settings_manager_storage']
offsets={'audio_uart_hand_snapshot_context':0,'g2_audio_log_timezone':0,
         'audio_settings_config_previous':4,'audio_settings_als_previous':24,
         'audio_settings_terminal_previous':28}
for name,offset in offsets.items():assert sym[name]==base_addr+offset,(name,sym.get(name))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after==set(offsets),(before-after,set(offsets))
assert not after-before
receipt={'round':1008,'status':'PASS_SETTINGS_MANAGER_STORAGE_BINDING',
         'component':'Apollo shared settings manager record and pointer-cell aliases',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_base':'0x200036fc','native_literal_addresses':['0x44a40c','0x4667f0','0x46c694','0x4f5e80'],
         'aliases':offsets,
         'validation':'Native base literals, M55 strict compile, alias offsets and five selected import bindings',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Producer initialization and exact native record allocation extent remain open',
                  'Final RAM placement/full map overlap and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
