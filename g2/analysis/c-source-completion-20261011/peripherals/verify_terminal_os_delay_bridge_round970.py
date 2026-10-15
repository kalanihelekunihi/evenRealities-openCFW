#!/usr/bin/env python3
"""Bind terminal mode-sync's osDelay name to the selected native osDelay body."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-os-delay-bridge-round970';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_os_delay_bridge.c'
obj=out/'terminal_os_delay_bridge.o'
base=root/'build/c-firmware/ble-param-reset-round969/apollo-main-ble-param-reset.o'
linked=out/'apollo-main-terminal-os-delay.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x449376-0x438000:0x449398-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
def symbols(path,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm',flag,str(path)],text=True).splitlines()}
assert symbols(obj,'-u')=={'audio_delay'}
assert 'audio_delay' in symbols(base,'--defined-only')
assert 'audio_os_delay' in symbols(obj,'--defined-only')
relocs=subprocess.check_output(['arm-none-eabi-objdump','-r',str(obj)],text=True)
assert relocs.count('audio_delay')==1,relocs
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before,after=symbols(base,'-u'),symbols(linked,'-u')
assert before-after=={'audio_os_delay'} and after-before==set(),(before-after,after-before)
receipt={'round':970,'status':'PASS_TERMINAL_OS_DELAY_BRIDGE','component':'Apollo terminal osDelay name bridge to selected 0x449376 source body',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'validation':'C bridge imports only selected audio_delay; one ARM relocation; linked object resolves terminal alias',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Alias linkage is source evidence, not a fresh native/C full-body replay','Final terminal callback and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after))
