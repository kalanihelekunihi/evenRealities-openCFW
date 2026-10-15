#!/usr/bin/env python3
"""Select Cordio timer helpers around Apollo-owned WsfTimerStop and locks."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/wsf-timer-helpers-round860';out.mkdir(parents=True,exist_ok=True)
src=root/'components/foundation/wsf_timer/wsf_timer_stop.c'
base_receipt=json.loads((root/'build/c-firmware/ready-event-provider-round859/receipt.json').read_text())
base=root/base_receipt['linked_object']
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
       '-std=c11','-ffreestanding','-fno-builtin','-O2']
def defined(obj):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines()}
normal=out/'wsf_timer_default.o';selected=out/'wsf_timer_selected.o'
subprocess.run(flags+['-c',str(src),'-o',str(normal)],check=True)
subprocess.run(flags+['-DOPENCFW_WSF_TIMER_EXTERNAL_STOP','-c',str(src),'-o',str(selected)],check=True)
shared={'WsfTimerStop','WsfTaskLock','WsfTaskUnlock'}
extra={'WsfQueueRemove','opencfw_wsf_timer_remove_raw','opencfw_radio_timer_gpio_shutdown_phase'}
assert shared|extra<=defined(normal)
assert extra<=defined(selected) and not shared&defined(selected)
assert shared<=defined(base) and not extra&defined(base)
linked=out/'apollo-main-wsf-timer-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(selected),'-o',str(linked)],check=True)
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
before=set(base_receipt.get('unresolved',[]))
if not before:
 before={line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after=set(imports)
receipt={'round':860,'status':'PASS_SELECTED_CORDIO_PROVIDER_RELOCATABLE_ONLY',
         'component':'Apollo Main Cordio timer provider',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'selected_flag':'OPENCFW_WSF_TIMER_EXTERNAL_STOP',
         'default_symbols':sorted(defined(normal)),'selected_symbols':sorted(defined(selected)),
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['FreeRTOS resume duplicate alternative remains excluded',
                  'WSF timer queue layout and runtime behavior require integrated validation',
                  'Final source catalog, image placement, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_WSF_TIMER_HELPERS',len(before-after),len(after-before),len(imports))
