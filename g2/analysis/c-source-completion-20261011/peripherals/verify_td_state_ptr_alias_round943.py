#!/usr/bin/env python3
"""Compile the Apollo state pointer alias and verify its official literal."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-state-alias-round943';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_state_ptr_alias1.c'
obj=out/'td_state_ptr_alias1.o'
base=root/'build/c-firmware/terminal-runtime-mapper-round942/apollo-main-terminal-runtime-mapper.o'
linked=out/'apollo-main-td-state-alias.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x597344-0x438000:0x59734a-0x438000]
assert native==bytes.fromhex('dff8c0087047')
literal=blob[0x597c08-0x438000:0x597c0c-0x438000]
assert int.from_bytes(literal,'little')==0x2010fd20
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_state_ptr_alias1'} and not after-before
receipt={'round':943,'status':'PASS_NATIVE_TD_STATE_POINTER_ALIAS','component':'Apollo td_state pointer alias 0x597344','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'validation':'Native literal 0x2010fd20 matches existing source-owned td_state base; C object links into selected Apollo object','linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Candidate session selector 0x5e505a and record status reader 0x597446 remain open','Final RAM placement/initialization and callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after))
