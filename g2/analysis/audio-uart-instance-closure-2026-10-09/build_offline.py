from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];C=R/'g2/components/audio/uart_instance_offline';O=Path('/tmp/opencfw-uart-instance');O.mkdir(exist_ok=True)
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ld='uart_thread_handler = 0x5417D7; osThreadNew = 0x4490E3; platform_log_flags = 0x43D0CF; platform_log_error = 0x43D575; compressed_log_output = 0x43CE9F; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }'
(O/'module.ld').write_text(ld)
flags=['-mcpu=cortex-m33','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib']
subprocess.run([str(gcc),*flags,'-I',str(C),str(C/'instance.c'),'-Wl,-T,'+str(O/'module.ld'),'-o',str(O/'instance.elf')],check=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec={'elf':str(O/'instance.elf'),'elf_sha256':sha(O/'instance.elf'),'gcc':str(gcc),'flags':flags,'link_script':ld,'sources':{str((C/'instance.c').relative_to(R)):sha(C/'instance.c'),str((C/'instance.h').relative_to(R)):sha(C/'instance.h')},'limits':'Direct wrapper invocation; thread creation and diagnostic sinks are explicit supplied boundaries.'}
(D/'reproduction-receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
