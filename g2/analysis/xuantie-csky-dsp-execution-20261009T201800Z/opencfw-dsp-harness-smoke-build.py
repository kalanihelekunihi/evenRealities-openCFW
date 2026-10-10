from pathlib import Path
import json,subprocess,hashlib
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';old=json.loads((d/'harness-build-results.json').read_text());rows=[]
for smoke in [True,False]:
 compile=next(x['command'] for x in old if '/out/harness.c' in x['command']);cmd=compile.copy()
 if smoke:cmd.insert(cmd.index('-c'),'-DSMOKE_ONLY=1')
 q=subprocess.run(cmd,capture_output=True,text=True);rows.append({'command':cmd,'returncode':q.returncode,'stderr':q.stderr});assert q.returncode==0,q.stderr
 link=old[-1]['command'].copy();name='smoke.elf' if smoke else 'harness.elf';link[link.index('/out/harness.elf')]='/out/'+name;q=subprocess.run(link,capture_output=True,text=True);rows.append({'command':link,'returncode':q.returncode,'stderr':q.stderr,'sha256':hashlib.sha256((d/name).read_bytes()).hexdigest()});assert q.returncode==0,q.stderr
(d/'smoke-and-corpus-build-results.json').write_text(json.dumps(rows,indent=2)+'\n');print('smoke and corpus linked')
