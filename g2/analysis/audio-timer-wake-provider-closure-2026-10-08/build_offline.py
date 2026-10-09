from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-timer-wake-providers');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
sources=[R/'g2/components/audio/timer_wake_providers_offline/unlock.c',R/'g2/components/foundation/freertos_ready/tasks_subset.c',R/'g2/components/foundation/freertos_ready/list_subset.c',R/'g2/components/audio/timer_aux_lifetime_offline/aux.c',R/'g2/components/audio/timer_wake_providers_offline/port.c',R/'g2/components/audio/timer_queue_wait_offline/wait.c',R/'g2/components/audio/delayed_block_offline/block.c',R/'g2/components/audio/timer_wake_providers_offline/sorted.c']
bindings={'stock_bad_critical_exit':0x4420f7,'opencfw_event_group_assert_failure':0x45537f}
bindings.update(dict(audio_aux_irq_context=0x44900f,audio_aux_get_id=0x47eb27,audio_aux_command=0x47e7b1,audio_aux_free=0x456211,audio_aux_suspend=0x454d7d,audio_aux_resume=0x454dcd,audio_aux_sample_time=0x47e917,audio_aux_list_remove=0x4560e9,audio_timer_list_remove=0x4560e9))

ld=O/'link.ld';ld.write_text(' '.join(f'{k} = {v:#x};' for k,v in bindings.items())+' audio_block_remove = uxListRemove; audio_block_sorted_insert = audio_public_list_insert; audio_timer_wait_enter = stock_enter_critical; audio_timer_wait_exit = stock_exit_critical; audio_timer_wait_unlock = audio_public_queue_unlock; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];elf=O/'wake.elf';subprocess.run([str(gcc),*flags,'-T',str(ld),*[str(p) for p in sources],'-o',str(elf)],check=True)
headers=[R/'g2/components/audio/timer_wake_providers_offline/unlock.h',R/'g2/components/foundation/freertos_ready/ready.h',R/'g2/components/foundation/freertos_ready/ready_compat.h',R/'g2/components/foundation/freertos_queue/queue.h',R/'g2/components/foundation/freertos_event_group/event_group.h',R/'g2/components/audio/timer_commands_offline/timer.h']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'reproduction-receipt.json').write_text(json.dumps({'elf':str(elf),'elf_sha256':h(elf),'sources':{str(p.relative_to(R)):h(p) for p in sources+headers},'bindings':bindings,'flags':flags,'gcc':str(gcc),'gcc_sha256':h(gcc),'link_script':ld.read_text()},indent=2)+'\n')
