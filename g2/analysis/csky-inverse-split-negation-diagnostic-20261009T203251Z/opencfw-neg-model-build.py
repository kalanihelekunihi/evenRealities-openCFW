from pathlib import Path
import subprocess,json,hashlib
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=Path(Path('/tmp/opencfw-neg-model-path').read_text());old=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';prior=r/'g2/analysis/nationalchip-dsp-complete-c-alternative-20261009T200634Z';j=json.loads((old/'harness-build-results.json').read_text());orig=next(x['command'] for x in j if '/out/harness.c' in x['command']);k=orig.index('/tool/bin/csky-abiv2-elf-gcc');base=orig[:k];base[base.index('type=bind,src='+str(old)+',dst=/out')]='type=bind,src='+str(d)+',dst=/out';flags=orig[k+1:orig.index('-c')];rows=[]
def run(args):
 cmd=base+args;q=subprocess.run(cmd,capture_output=True,text=True);rows.append({'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});assert q.returncode==0,q.stderr
for name in ['inverse_split_diagnostic.c','diagnostic-harness.c']:
 run(['/tool/bin/csky-abiv2-elf-gcc']+flags+['-std=gnu99','-c','/out/'+name,'-o','/out/'+name+'.o'])
run(['/tool/bin/csky-abiv2-elf-objcopy','--redefine-sym','csky_split_rifft_q15=diagnostic_csky_split_rifft_q15','/repo/'+str((prior/'csky_rfft_q15.o').relative_to(r)),'/out/diagnostic-wrapper.o'])
run(['/tool/bin/csky-abiv2-elf-objcopy','--redefine-sym','csky_split_rifft_q15=diagnostic_csky_split_rifft_q15','/repo/'+str((old/'stage-main.o').relative_to(r)),'/out/diagnostic-stage-main.o'])
original_link=j[-1]['command'];start=original_link.index('/out/startup.o');deps=original_link[start+2:];deps=[x if x.startswith('/repo/') else '/repo/'+str((old/x.removeprefix('/out/')).relative_to(r)) for x in deps];deps=[x for x in deps if x!='/repo/'+str((prior/'csky_rfft_q15.o').relative_to(r))];deps+=['/out/inverse_split_diagnostic.c.o','/out/diagnostic-wrapper.o']
for name,main in [('diagnostic.elf','diagnostic-harness.c.o'),('diagnostic-stages.elf','diagnostic-stage-main.o')]:
 run(['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-T,/out/harness.ld','-o','/out/'+name,'/repo/'+str((old/'startup.o').relative_to(r)),'/out/'+main]+deps)
(d/'build-results.json').write_text(json.dumps(rows,indent=2)+'\n');print('linked',d)
