#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
D=Path(__file__).resolve().parent;R=D.parents[2];O=D/'build';O.mkdir(exist_ok=True)
G='/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc'
S=[R/'g2/components/case/source_candidate_20261010/evidenced_providers.c',R/'g2/components/case/event_flags_offline/events.c']
L=O/'behavior.ld'
L.write_text('''xEventGroupGetBitsFromISR = 0x0800c4cd;
xEventGroupClearBitsFromISR = 0x0800c479;
xEventGroupClearBits = 0x0800c44d;
xEventGroupSetBitsFromISR = 0x0800c569;
xEventGroupSetBits = 0x0800c4df;
SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
''')
E=O/'behavior.elf';cmd=[G,'-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(L),*[str(s) for s in S],'-o',str(E)]
r=subprocess.run(cmd,text=True,capture_output=True);assert r.returncode==0,r.stderr
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'behavior-build-receipt.json').write_text(json.dumps({'python':sys.executable,'gcc':G,'gcc_sha256':h(Path(G)),'gcc_version':subprocess.run([G,'--version'],capture_output=True,text=True).stdout.splitlines()[0],'command':cmd,'sources':[{'path':str(s.relative_to(R)),'sha256':h(s)} for s in S],'link_script_sha256':h(L),'elf':str(E),'elf_sha256':h(E)},indent=2)+'\n')
print(E)
