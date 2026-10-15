#!/usr/bin/env python3
"""Bind the already parity-checked native persistence gateway into the selected Apollo object."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-settings-persist-bridge-round990';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_settings_persist_bridge.c'
terminal=root/'components/audio/uart_thread_source_candidate/terminal_command_5e8846.c'
base=root/'build/c-firmware/callback-mgr-delete-node-round989/apollo-main-callback-mgr-delete-node.o'
obj=out/'terminal_settings_persist_bridge.o';fresh=out/'terminal_command_5e8846.o'
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c']
for s,o in ((src,obj),(terminal,fresh)):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
subprocess.run([sys.executable,str(root/'analysis/c-source-completion-20261011/peripherals/verify_ring_wear_persist_native.py')],check=True)
linked=out/'apollo-main-terminal-settings-persist-bridge.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after in ({'audio_settings_persist_event'},set()) and not after-before,(before-after,after-before)
assert 'audio_uart_ring_wear_persist_48eb32' in subprocess.check_output(['arm-none-eabi-nm',str(linked)],text=True)
assert 'audio_uart_ring_wear_persist_48eb32' in subprocess.check_output(['arm-none-eabi-nm','-u',str(fresh)],text=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
receipt={'round':990,'status':'PASS_TERMINAL_SETTINGS_PERSIST_BRIDGE','component':'Apollo terminal settings persistence gateway 0x48eb32','source':[str(p.relative_to(root)) for p in (src,terminal)],'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,terminal)},'official_image_sha256':hashlib.sha256(blob).hexdigest(),'validation':'M55 strict compile, selected-object import binding, prior six-case native/C gateway parity','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Existing gateway child behavior remains bounded','Full image layout and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
