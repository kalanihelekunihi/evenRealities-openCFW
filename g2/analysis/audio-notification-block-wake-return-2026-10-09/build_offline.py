from pathlib import Path
import subprocess, json, hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-notification-roundtrip');O.mkdir(exist_ok=True)
G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin')
ld=O/'link.ld';ld.write_text('audio_irq_context = 0x44900F; audio_tick = 0x454EFF; audio_enter_critical = 0x4420D1; audio_exit_critical = 0x4420E9; audio_block_ticks = audio_block_current; audio_yield = 0x4420BD; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];elf=O/'roundtrip.elf'
src=[R/'g2/components/audio/notification_wait_offline/wait.c',R/'g2/components/audio/notification_block_offline/block.c',R/'g2/components/audio/uart_rx_notifier_offline/notify.c',R/'g2/components/audio/uart_rx_stream_offline/support.c',R/'g2/components/audio/tick_expiry_offline/tick.c']
subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),*map(str,src),'-o',str(elf)],check=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();headers=[R/'g2/components/audio/notification_wake_offline/wake.h',R/'g2/components/audio/notification_block_offline/block.h',R/'g2/components/audio/uart_rx_notifier_offline/notify.h']
(D/'reproduction-receipt.json').write_text(json.dumps({'elf':str(elf),'elf_sha256':h(elf),'gcc':str(G/'arm-none-eabi-gcc'),'flags':flags,'link_script':ld.read_text(),'sources':{str(p.relative_to(R)):h(p) for p in src+headers},'limits':'Fixture explicitly orders block, notifier or tick, then resumes the saved wait continuation. No exception delivery/context switch is simulated.'},indent=2)+'\n')
