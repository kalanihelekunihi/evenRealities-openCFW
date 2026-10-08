from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];O=Path('/tmp/opencfw-early-pcm-gpu');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');src=R/'g2/components/audio/early_pcm_gpu_offline/gpu.c';classifier=R/'g2/components/audio/platform_callbacks_offline/classify.c'
callbacks=R/'g2/components/audio/platform_callbacks_offline/callbacks.c'
bindings=dict(stock_delay=0x4807a1,stock_ton_update=0x4803c3,stock_buck_enable=0x47fe6d,stock_save_irq=0x473941,stock_temperature_apply=0x5a001d,stock_stimer_running=0x48d621)
link=O/'link.ld';link.write_text('early_zero = pcm_early_off; early_other = pcm_early_on; middle_action0 = pcm_sleep; middle_zero = pcm_middle_off; middle_other = pcm_middle_on; middle_action2 = pcm_temperature; pcm_early_control = audio_platform_early_control; pcm_middle_control = audio_platform_middle_control; '+' '.join(f'{n} = {v:#x};' for n,v in bindings.items())+' SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
flags=['-mcpu=cortex-m33','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-fshort-enums'];elf=O/'control.elf';subprocess.run([str(gcc),*flags,'-T',str(link),str(src),str(callbacks),'-o',str(elf)],check=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(sources={str(p.relative_to(R)):h(p) for p in [src,src.with_suffix('.h'),callbacks,callbacks.with_suffix('.h')]},gcc=str(gcc),gcc_sha256=h(gcc),flags=flags,elf=str(elf),elf_sha256=h(elf),bindings=bindings,link_script=link.read_text()),indent=2)+'\n')
