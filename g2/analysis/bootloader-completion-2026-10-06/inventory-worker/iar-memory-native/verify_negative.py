from pathlib import Path
import subprocess,json
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());B=R/'g2/build/bootloader-completion/iar-memory-native-qemu';T=Path('/tmp/opencfw-memory-mutants');T.mkdir(exist_ok=True);src=(R/'g2/components/bootloader/initializer_callbacks/iar_memory_native/memory.c').read_text();flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin'];rows=[]
for name,old,new in [('copy-cursor','p+(count&~1u)','p+count'),('fill-byte','(uint8_t)value','(uint8_t)(value^1u)')]:
 p=T/(name+'.c');assert old in src;p.write_text(src.replace(old,new));o=T/(name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True);elf=T/(name+'.elf');subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(N/'qemu.ld'),str(B/'start.o'),str(B/'harness.o'),str(B/'abi.o'),str(o),'-o',str(elf)],check=True,capture_output=True)
 r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(N/'verify_qemu.py'),'--elf',str(elf),'--output',str(N/(name+'-failure.json'))],capture_output=True,text=True);assert r.returncode!=0;rows.append(dict(control=name,rejected=True,receipt=name+'-failure.json'))
(N/'negative-controls.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
