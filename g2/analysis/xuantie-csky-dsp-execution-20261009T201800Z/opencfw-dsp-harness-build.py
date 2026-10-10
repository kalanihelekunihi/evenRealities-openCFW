from pathlib import Path
import json,subprocess,hashlib
from elftools.elf.elffile import ELFFile
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';prior=r/'g2/analysis/nationalchip-dsp-complete-c-alternative-20261009T200634Z';asm=r/'g2/analysis/nationalchip-dsp-source-rebuild-20261009T194601Z';j=json.loads((prior/'link-completion-results.json').read_text());cmd=j['additional_compile'][0]['command'];k=cmd.index('/tool/bin/csky-abiv2-elf-gcc');base=cmd[:k];base[base.index('type=bind,src='+str(prior)+',dst=/out')]='type=bind,src='+str(d)+',dst=/out';flags=cmd[k+1:cmd.index('-c')];rows=[]
def run(args):
 q=subprocess.run(base+args,capture_output=True,text=True);rows.append({'command':base+args,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});assert q.returncode==0,q.stderr
symbols=j['link']['defined_symbols'];(d/'rename-symbols.txt').write_text(''.join(n+' asm_'+n+'\n' for n in symbols))
objs=[]
for name in ['csky_cfft_radix4_q15.o','csky_rfft_q15.o','csky_shift_q15.o','csky_abs_max_q15.o','csky_copy_q15.o','csky_fill_q15.o','csky_bitreversal2.o']:
 out='asm_'+name;run(['/tool/bin/csky-abiv2-elf-objcopy','--redefine-syms=/out/rename-symbols.txt','/repo/'+str((asm/name).relative_to(r)),'/out/'+out]);objs.append('/out/'+out)
for name in ['csky_cfft_q15.o','csky_rfft_q15.o']:
 out='asm_dispatch_'+name;run(['/tool/bin/csky-abiv2-elf-objcopy','--redefine-syms=/out/rename-symbols.txt','/repo/'+str((prior/name).relative_to(r)),'/out/'+out]);objs.append('/out/'+out)
p=r/'third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source.asm/TransformFunctions/csky_cfft_q15.S';run(['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-c','/repo/'+str(p.relative_to(r)),'-o','/out/assembly-radix4by2.o']);run(['/tool/bin/csky-abiv2-elf-objcopy','--redefine-syms=/out/rename-symbols.txt','/out/assembly-radix4by2.o','/out/asm_radix4by2.o']);objs.append('/out/asm_radix4by2.o')
run(['/tool/bin/csky-abiv2-elf-gcc']+flags+['-std=gnu99','-c','/out/harness.c','-o','/out/harness.o']);run(['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-c','/out/startup.S','-o','/out/startup.o']);cobjs=['/repo/'+str(p.relative_to(r)) for p in prior.glob('*.o') if p.name!='csky_bitreversal.o'];run(['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-T,/out/harness.ld','-Wl,-Map,/out/harness.map','-o','/out/harness.elf','/out/startup.o','/out/harness.o']+cobjs+objs);(d/'harness-build-results.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS',hashlib.sha256((d/'harness.elf').read_bytes()).hexdigest())
