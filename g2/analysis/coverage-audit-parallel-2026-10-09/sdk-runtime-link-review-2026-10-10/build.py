from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).parent;inc=Path('g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi/arm-none-eabi/include');recipes=[]
def run(cmd,out):
 r=subprocess.run(cmd,capture_output=True,text=True);(D/out).write_text(r.stdout+r.stderr);recipes.append({'command':cmd,'exit':r.returncode,'receipt':out});return r
common=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-I'+str(D),'-isystem',str(inc)]
for variant in ['plain','apollo5-aligned']:
 flags=['-mfloat-abi=hard']+(['-DAM_PART_APOLLO5_API'] if variant!='plain' else [])
 r=run(common+flags+['-c',str(D/'am_util_stdio.c'),'-o',str(D/f'{variant}-stdio.o')],f'{variant}-compile.txt');assert r.returncode==0
 r=run(common+flags+['-c',str(D/'placement-probe.c'),'-o',str(D/f'{variant}-probe.o')],f'{variant}-probe-compile.txt');assert r.returncode==0
 cmd=['arm-none-eabi-ld','-T',str(D/'gcc/linker_script.ld'),'-e','placement_probe','-Map='+str(D/f'{variant}.map'),str(D/f'{variant}-probe.o'),str(D/f'{variant}-stdio.o'),'-o',str(D/f'{variant}.elf')];r=run(cmd,f'{variant}-link.txt');assert r.returncode==0,r.stderr
 run(['arm-none-eabi-nm','-u',str(D/f'{variant}.elf')],f'{variant}-undefined.txt');run(['arm-none-eabi-readelf','-A','-S','-l',str(D/f'{variant}.elf')],f'{variant}-elf.txt');run(['arm-none-eabi-nm','-n',str(D/f'{variant}.elf')],f'{variant}-symbols.txt')
r=run(common+['-mfloat-abi=soft','-c',str(D/'placement-probe.c'),'-o',str(D/'soft-probe.o')],'soft-probe-compile.txt');assert r.returncode==0
r=run(['arm-none-eabi-ld','-T',str(D/'gcc/linker_script.ld'),'-e','placement_probe','-Map='+str(D/'mixed-abi.map'),str(D/'soft-probe.o'),str(D/'plain-stdio.o'),'-o',str(D/'mixed-abi.elf')],'mixed-abi-rejection.txt');assert r.returncode!=0
r=run(common+['-mfloat-abi=softfp','-c',str(D/'am_util_stdio.c'),'-o',str(D/'softfp-stdio.o')],'softfp-stdio-compile.txt');assert r.returncode==0
r=run(['arm-none-eabi-ld','-T',str(D/'gcc/linker_script.ld'),'-e','tlsf_create','-Map='+str(D/'tlsf-sdk-negative.map'),str(Path('g2/analysis/tlsf-main-source-comparison-20261010-implementation/comparator.o')),str(D/'softfp-stdio.o'),'-o',str(D/'tlsf-sdk-negative.elf')],'tlsf-sdk-negative.txt');assert r.returncode!=0
(D/'recipes.json').write_text(json.dumps(recipes,indent=2)+'\n');print('Two authentic formatter/SDK-script links pass; mixed ABI rejects; no execution')
