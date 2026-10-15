#!/usr/bin/env python3
"""Select FreeRTOS event-list provider while retaining Apollo's task-count getter."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ready-event-provider-round859';out.mkdir(parents=True,exist_ok=True)
src=root/'components/foundation/freertos_ready/tasks_subset.c'
base_receipt=json.loads((root/'build/c-firmware/foundation-integration-round858/link-receipt.json').read_text())
base=root/base_receipt['linked_object']
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
       '-std=c11','-ffreestanding','-fno-builtin','-O2']
def defined(obj):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines()}
normal=out/'tasks_subset_default.o';selected=out/'tasks_subset_selected.o'
subprocess.run(flags+['-c',str(src),'-o',str(normal)],check=True)
subprocess.run(flags+['-DOPENCFW_READY_EXTERNAL_TASK_COUNT','-c',str(src),'-o',str(selected)],check=True)
assert {'opencfw_ready_remove_event_list','uxTaskGetNumberOfTasks'}<=defined(normal)
assert 'opencfw_ready_remove_event_list' in defined(selected)
assert 'uxTaskGetNumberOfTasks' not in defined(selected)
assert 'uxTaskGetNumberOfTasks' in defined(base)
linked=out/'apollo-main-ready-event-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(selected),'-o',str(linked)],check=True)
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
before=set(base_receipt['unresolved']);after=set(imports)
assert 'opencfw_ready_remove_event_list' in before and 'opencfw_ready_remove_event_list' not in after
assert 'uxTaskGetNumberOfTasks' in defined(linked)
receipt={'round':859,'status':'PASS_SELECTED_FREERTOS_PROVIDER_RELOCATABLE_ONLY',
         'component':'Apollo Main FreeRTOS ready-list provider',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'selected_flag':'OPENCFW_READY_EXTERNAL_TASK_COUNT',
         'default_symbols':sorted(defined(normal)),'selected_symbols':sorted(defined(selected)),
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Other two foundation alternative files remain excluded',
                  'Final FreeRTOS state layout and runtime scheduling remain unproven',
                  'Full source catalog, image placement, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_READY_EVENT_PROVIDER',len(before-after),len(after-before),len(imports))
