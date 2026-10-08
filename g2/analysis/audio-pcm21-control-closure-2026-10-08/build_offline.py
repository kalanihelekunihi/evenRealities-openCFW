from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-pcm21-control');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');src=R/'g2/components/audio/pcm21_control_offline/control.c';classifier=R/'g2/components/audio/platform_callbacks_offline/classify.c'
bindings=dict(stock_save_irq=0x473941,stock_prepare=0x5a0c21,stock_change_state=0x5a0d45,stock_plan=0x5a13e9,stock_apply=0x5a0fc5)
link=O/'link.ld';link.write_text('pcm21_classify = audio_platform_classify; '+' '.join(f'{n} = {v:#x};' for n,v in bindings.items())+' SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m33','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-fshort-enums'];elf=O/'control.elf';subprocess.run([str(gcc),*flags,'-T',str(link),str(src),str(classifier),'-o',str(elf)],check=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(sources={str(p.relative_to(R)):h(p) for p in [src,src.with_suffix('.h'),classifier]},gcc=str(gcc),gcc_sha256=h(gcc),flags=flags,elf=str(elf),elf_sha256=h(elf),bindings=bindings,link_script=link.read_text()),indent=2)+'\n')
