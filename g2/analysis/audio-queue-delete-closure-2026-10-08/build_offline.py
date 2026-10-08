import subprocess
from pathlib import Path
out=Path('/tmp/opencfw-audio-delete');out.mkdir(exist_ok=True)
(out/'link.ld').write_text('audio_irq_context = 0x44900f; audio_suspend = 0x454d7d; audio_resume = 0x454dcd; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
subprocess.run(['/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc','-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(out/'link.ld'),'g2/components/audio/queue_delete_offline/delete.c','-o',str(out/'delete.elf')],check=True)
