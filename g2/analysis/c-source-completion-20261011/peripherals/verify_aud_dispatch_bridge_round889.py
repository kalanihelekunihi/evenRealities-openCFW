#!/usr/bin/env python3
"""Bind native AUD_SendMessage to the already selected, verified provider."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/aud-dispatch-bridge-round889';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/aud_message_dispatch_bridge.c'
provider=root/'components/audio/audio_submit_source_candidate/submit.c'
obj=out/'aud_message_dispatch_bridge.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x53c638-0x438000:0x53c6b2-0x438000]
assert hashlib.sha256(native).hexdigest()=='1ba20aa804d5938a30b726518252b676b3bd75b0999ee56f724b1ca20f0b689c'
suite=subprocess.run(['python3',str(root/'analysis/c-source-completion-20261011/peripherals/verify_audio_submit.py')],
                     text=True,capture_output=True,check=True)
assert 'PASS_AUDIO_SUBMIT 96' in suite.stdout,suite.stdout
base=root/'build/c-firmware/registry-audm-round888/apollo-main-registry-audm.o'
linked=out/'apollo-main-aud-dispatch-bridge.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before-after=={'audio_aud_message_dispatch_53c638'} and not after-before
definitions={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(base)],text=True).splitlines()}
assert 'stock_audio_submit' in definitions
receipt={'round':889,'status':'PASS_AUD_DISPATCH_PROVIDER_BINDING',
         'component':'Apollo audio manager message dispatch',
         'bridge_source':str(src.relative_to(root)),
         'bridge_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'provider_source':str(provider.relative_to(root)),
         'provider_source_sha256':hashlib.sha256(provider.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'existing_provider_native_cases':96,
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'registry_callback_bodies_complete':10,'registry_callback_bodies_total':64,
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Audio queue/runtime and 54 registry callback bodies remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_AUD_DISPATCH_PROVIDER_BINDING',len(after))
