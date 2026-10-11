#!/usr/bin/env python3
"""Build the current Bootloader GX graph for the M33 FP-capable stock oracle."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];O=H/'gx-split-trial';O.mkdir(exist_ok=True)
C=R/'g2/components/bootloader';B=C/'source_candidate_20261010';M=C/'clock_manager'
sources=[C/'initializer_callbacks/startup_runtime.c',B/'gx_event.c',B/'gx_adapters.c',B/'gx_children.c',B/'spot_trim.c',C/'platform_control/critical_save.S']+[M/(n+'.c') for n in ('clock_manager','clock_class_providers','clock_class_provider2','clock_class_provider4','clock_class_provider5','clock_class_provider6')]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();objects=[];commands=[]
for i,p in enumerate(sources):
 o=O/f'production_{i}.o';cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-I'+str(C/'initializer_callbacks'),'-c',str(p),'-o',str(o)]
 subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);objects.append(o);commands.append(cmd)
elf=O/'gx_dispatch_source.elf';cmd=['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_startup_spot_dispatch','--gc-sections','--undefined=opencfw_boot_spot_state_power_event','--defsym=hw_state_compose_42bdf0_native=0x30001','--unresolved-symbols=ignore-all','-o',str(elf),*[str(o) for o in objects]]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);commands.append(cmd)
receipt=dict(status='PASS',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),source_sha256={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},commands=commands,limits='M33 hard-float oracle build, using exact selected C source plus selected clock and trim graph; M55 archive compilation is separate. hw_state_compose first callback is a controlled installed-table boundary. Other unresolved startup table pointers are not invoked here.')
(O/'production-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS GX production oracle build',receipt['elf_sha256'])
