from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-clock-reset-gates');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');src=R/'g2/components/audio/clock_reset_gates_offline/gates.c';link=O/'link.ld';link.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m33','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-fshort-enums'];elf=O/'control.elf';subprocess.run([str(gcc),*flags,'-T',str(link),str(src),'-o',str(elf)],check=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(sources={str(p.relative_to(R)):h(p) for p in [src,src.with_suffix('.h')]},gcc=str(gcc),gcc_sha256=h(gcc),flags=flags,elf=str(elf),elf_sha256=h(elf),link_script=link.read_text()),indent=2)+'\n')
