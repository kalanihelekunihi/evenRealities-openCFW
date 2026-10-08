from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-transition-timer');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');src=R/'g2/components/audio/transition_timer_offline/transition.c'
bindings=dict(stock_delay_us=0x4807a1,stock_timer_start=0x480241,stock_clock_release=0x4c4531,stock_ton_adjust=0x5a423d,stock_delay_status=0x4807fd,stock_save_irq=0x473941)
link=O/'link.ld';link.write_text(' '.join(f'{n} = {v:#x};' for n,v in bindings.items())+' SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m33','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-fshort-enums'];elf=O/'transition.elf';subprocess.run([str(gcc),*flags,'-T',str(link),str(src),'-o',str(elf)],check=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(source=str(src.relative_to(R)),source_sha256=h(src),header_sha256=h(src.with_suffix('.h')),gcc=str(gcc),gcc_sha256=h(gcc),flags=flags,elf=str(elf),elf_sha256=h(elf),bindings=bindings,link_script=link.read_text()),indent=2)+'\n')
