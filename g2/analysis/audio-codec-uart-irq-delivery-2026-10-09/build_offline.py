from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'g2/components/audio/codec_uart_irq_offline';O=Path('/tmp/opencfw-codec-irq');O.mkdir(exist_ok=True);G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin')
ld=O/'link.ld';ld.write_text('codec_irq_status = 0x58E80F; codec_irq_clear = 0x58E7E5; codec_irq_service = 0x58E861; codec_fifo_read = 0x58E2D9; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m33','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];elf=O/'irq.elf';src=[S/'irq.c',R/'g2/components/audio/codec_uart_lifecycle_offline/lifecycle.c',R/'g2/components/audio/uart_rx_consumer_offline/ring.c']
# Lifecycle's unused external providers need link identities but are never reached.
ld.write_text('codec_hal_power = 0x58DBB9; codec_gpio_config = 0x480F0D; codec_hal_configure = 0x58E09F; '+ld.read_text())
subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),*map(str,src),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'reproduction-receipt.json').write_text(json.dumps({'elf':str(elf),'elf_sha256':h(elf),'sources':{str(p.relative_to(R)):h(p) for p in src+[S/'irq.h']},'gcc':str(G/'arm-none-eabi-gcc'),'flags':flags,'link_script':ld.read_text(),'limits':'HAL status/clear/service/FIFO reads are explicit supplied boundaries. Direct IRQ entry is invoked by fixture, not vector delivery.'},indent=2)+'\n')
